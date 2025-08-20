from typing import List, Dict, Any
from ..schemas.common import CandidateProfile, JobProfile, JobSkillReq
from ..schemas.match import MatchResult, MatchReason
from ..utils.embeddings import cosine_similarity, text_to_vec
from ..utils.io import load_yaml, get_config_path
import rapidfuzz
import re
import re

class Matcher:
    """Match candidates to jobs based on skills, projects, education, and constraints."""
    
    def __init__(self):
        self.weights_config = self._load_weights_config()
    
    def _load_weights_config(self) -> Dict[str, Any]:
        """Load matching weights configuration."""
        config_path = get_config_path("match_weights.yaml")
        return load_yaml(str(config_path))
    
    def score_candidate_to_job(self, candidate: CandidateProfile, job: JobProfile, weights_cfg: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Score a candidate against a job.
        
        Returns:
            Dict with 'score', 'reasons', and 'gaps'
        """
        if weights_cfg is None:
            weights_cfg = self.weights_config
        
        # Check hard constraints first
        hard_constraints = weights_cfg.get('thresholds', {}).get('hard_constraints', [])
        for constraint in hard_constraints:
            if constraint == 'location':
                if candidate.location and job.location:
                    if candidate.location.lower() != job.location.lower():
                        return {
                            'score': 0.0,
                            'reasons': [MatchReason(
                                feature='location',
                                weight=0.0,
                                note=f"Location mismatch: {candidate.location} vs {job.location}"
                            )],
                            'gaps': [f"Location: {candidate.location} vs {job.location}"]
                        }
        
        # Calculate component scores
        skills_score, skills_reasons, skills_gaps = self._score_skills(candidate, job, weights_cfg)
        projects_score, projects_reasons = self._score_projects(candidate, job, weights_cfg)
        education_score, education_reasons = self._score_education(candidate, job, weights_cfg)
        experience_score, experience_reasons = self._score_experience(candidate, job, weights_cfg)
        domain_score, domain_reasons = self._score_domain(candidate, job, weights_cfg)
        location_score, location_reasons = self._score_location(candidate, job, weights_cfg)
        
        # Weighted combination
        weights = weights_cfg.get('weights', {})
        final_score = (
            skills_score * weights.get('skills', 0.40) +
            projects_score * weights.get('projects', 0.25) +
            education_score * weights.get('education', 0.20) +
            experience_score * weights.get('experience', 0.10) +
            domain_score * weights.get('domain', 0.03) +
            location_score * weights.get('location', 0.02)
        )
        
        # Combine all reasons
        all_reasons = skills_reasons + projects_reasons + education_reasons + experience_reasons + domain_reasons + location_reasons
        
        return {
            'score': round(final_score, 4),
            'reasons': all_reasons,
            'gaps': skills_gaps
        }
    
    def _score_skills(self, candidate: CandidateProfile, job: JobProfile, weights_cfg: Dict[str, Any]) -> tuple:
        """Score skills match between candidate and job."""
        reasons = []
        gaps = []
        
        # Get candidate skills as set for easy lookup
        candidate_skills = {skill.canonical.lower(): skill.level for skill in candidate.skills}
        
        # Check required skills
        required_score = 0.0
        total_required = len(job.required)
        
        for req in job.required:
            skill_name = req.skill.lower()
            min_level = req.min_level
            
            if skill_name in candidate_skills:
                candidate_level = candidate_skills[skill_name]
                if candidate_level >= min_level:
                    required_score += 1.0
                    reasons.append(MatchReason(
                        feature='skills',
                        weight=1.0,
                        note=f"Required skill '{req.skill}' met (level {candidate_level} >= {min_level})"
                    ))
                else:
                    # Partial credit for having skill but below level
                    partial_score = candidate_level / min_level
                    required_score += partial_score
                    reasons.append(MatchReason(
                        feature='skills',
                        weight=partial_score,
                        note=f"Required skill '{req.skill}' partially met (level {candidate_level} < {min_level})"
                    ))
                    gaps.append(f"Skill '{req.skill}' level {candidate_level} < required {min_level}")
            else:
                gaps.append(f"Missing required skill: {req.skill}")
        
        # Calculate final skills score
        skills_score = required_score / total_required if total_required > 0 else 0.0
        
        # Bonus for nice-to-have skills
        nice_bonus = 0.0
        for nice_skill in job.nice:
            if nice_skill.lower() in candidate_skills:
                nice_bonus += 0.1  # Small bonus for each nice-to-have skill
                reasons.append(MatchReason(
                    feature='skills',
                    weight=0.1,
                    note=f"Nice-to-have skill '{nice_skill}' present"
                ))
        
        final_skills_score = min(1.0, skills_score + nice_bonus)
        
        return final_skills_score, reasons, gaps
    
    def _score_projects(self, candidate: CandidateProfile, job: JobProfile, weights_cfg: Dict[str, Any]) -> tuple:
        """Score project relevance to job requirements."""
        reasons = []
        
        if not candidate.projects:
            return 0.0, reasons
        
        # Extract key terms from job title and requirements
        job_keywords = self._extract_job_keywords(job)
        
        relevant_projects = 0
        total_projects = len(candidate.projects)
        
        for project in candidate.projects:
            project_lower = project.lower()
            
            # Check for keyword matches
            keyword_matches = 0
            for keyword in job_keywords:
                if keyword.lower() in project_lower:
                    keyword_matches += 1
            
            # Consider project relevant if it has at least 2 keyword matches
            if keyword_matches >= 2:
                relevant_projects += 1
                reasons.append(MatchReason(
                    feature='projects',
                    weight=1.0,
                    note=f"Relevant project: {project[:50]}{'...' if len(project) > 50 else ''}"
                ))
            elif keyword_matches == 1:
                relevant_projects += 0.5
                reasons.append(MatchReason(
                    feature='projects',
                    weight=0.5,
                    note=f"Partially relevant project: {project[:50]}{'...' if len(project) > 50 else ''}"
                ))
        
        # Calculate project score
        project_score = relevant_projects / total_projects if total_projects > 0 else 0.0
        
        # Add summary reason if there are relevant projects
        if relevant_projects > 0:
            reasons.insert(0, MatchReason(
                feature='projects',
                weight=project_score,
                note=f"Found {relevant_projects} relevant projects out of {total_projects} total"
            ))
        
        return project_score, reasons
    
    def _score_education(self, candidate: CandidateProfile, job: JobProfile, weights_cfg: Dict[str, Any]) -> tuple:
        """Score education relevance to job requirements."""
        reasons = []
        
        if not candidate.education:
            return 0.0, reasons
        
        # Extract education keywords that are relevant to the job
        job_keywords = self._extract_job_keywords(job)
        education_keywords = self._get_education_keywords()
        
        relevant_education = 0
        total_education = len(candidate.education)
        
        for edu in candidate.education:
            edu_lower = edu.lower()
            
            # Check for degree level relevance
            degree_score = self._score_degree_level(edu_lower, job.title.lower())
            
            # Check for field relevance
            field_score = 0.0
            for keyword in job_keywords:
                if keyword.lower() in edu_lower:
                    field_score += 0.3
            
            # Check for education-specific keywords
            for edu_keyword in education_keywords:
                if edu_keyword.lower() in edu_lower:
                    field_score += 0.2
            
            # Calculate overall education item score
            item_score = min(1.0, degree_score + field_score)
            relevant_education += item_score
            
            if item_score > 0.5:
                reasons.append(MatchReason(
                    feature='education',
                    weight=item_score,
                    note=f"Relevant education: {edu[:50]}{'...' if len(edu) > 50 else ''}"
                ))
        
        # Calculate education score
        education_score = relevant_education / total_education if total_education > 0 else 0.0
        
        # Add summary reason if there's relevant education
        if relevant_education > 0:
            reasons.insert(0, MatchReason(
                feature='education',
                weight=education_score,
                note=f"Education relevance score: {relevant_education:.1f} out of {total_education} items"
            ))
        
        return education_score, reasons
    
    def _extract_job_keywords(self, job: JobProfile) -> List[str]:
        """Extract relevant keywords from job title and requirements."""
        keywords = []
        
        # Extract from job title
        title_words = re.findall(r'\b\w+\b', job.title.lower())
        keywords.extend([word for word in title_words if len(word) > 3])
        
        # Extract from required skills
        for req in job.required:
            keywords.append(req.skill.lower())
        
        # Extract from nice-to-have skills
        for skill in job.nice:
            keywords.append(skill.lower())
        
        # Add common job-related terms
        common_terms = ['data', 'software', 'web', 'mobile', 'cloud', 'database', 'api', 'frontend', 'backend', 'fullstack']
        keywords.extend(common_terms)
        
        return list(set(keywords))  # Remove duplicates
    
    def _get_education_keywords(self) -> List[str]:
        """Get education-related keywords for matching."""
        return [
            'computer science', 'software engineering', 'information technology', 'data science',
            'computer engineering', 'electrical engineering', 'mathematics', 'statistics',
            'business', 'management', 'economics', 'finance', 'marketing',
            'bachelor', 'master', 'phd', 'degree', 'certification', 'diploma'
        ]
    
    def _score_degree_level(self, education_text: str, job_title: str) -> float:
        """Score education level relevance to job seniority."""
        # Higher degrees for senior positions
        if any(term in job_title for term in ['senior', 'lead', 'principal', 'manager', 'director']):
            if any(term in education_text for term in ['master', 'phd', 'doctorate']):
                return 1.0
            elif any(term in education_text for term in ['bachelor', 'degree']):
                return 0.7
            else:
                return 0.3
        else:
            # Entry/mid-level positions
            if any(term in education_text for term in ['bachelor', 'degree', 'master']):
                return 1.0
            else:
                return 0.5

    def _score_experience(self, candidate: CandidateProfile, job: JobProfile, weights_cfg: Dict[str, Any]) -> tuple:
        """Score experience match."""
        reasons = []
        
        # Simple heuristic: count relevant roles
        relevant_roles = 0
        for role in candidate.roles:
            role_title = role.title.lower()
            job_title = job.title.lower()
            
            # Check if role title contains job-related keywords
            if any(keyword in role_title for keyword in ['engineer', 'developer', 'analyst', 'manager']):
                if any(keyword in job_title for keyword in ['engineer', 'developer', 'analyst', 'manager']):
                    relevant_roles += 1
        
        # Normalize to 0-1 score
        experience_score = min(1.0, relevant_roles / 3.0)  # Cap at 3 relevant roles
        
        if relevant_roles > 0:
            reasons.append(MatchReason(
                feature='experience',
                weight=experience_score,
                note=f"Found {relevant_roles} relevant roles"
            ))
        
        return experience_score, reasons
    
    def _score_domain(self, candidate: CandidateProfile, job: JobProfile, weights_cfg: Dict[str, Any]) -> tuple:
        """Score domain/department match."""
        reasons = []
        
        if not candidate.dept or not job.dept:
            return 0.5, reasons  # Neutral score if missing
        
        # Use fuzzy string matching
        similarity = rapidfuzz.fuzz.ratio(candidate.dept.lower(), job.dept.lower()) / 100.0
        
        if similarity > 0.7:
            reasons.append(MatchReason(
                feature='domain',
                weight=similarity,
                note=f"Department match: {candidate.dept} vs {job.dept}"
            ))
        
        return similarity, reasons
    
    def _score_location(self, candidate: CandidateProfile, job: JobProfile, weights_cfg: Dict[str, Any]) -> tuple:
        """Score location match."""
        reasons = []
        
        if not candidate.location or not job.location:
            return 0.5, reasons  # Neutral score if missing
        
        # Exact match
        if candidate.location.lower() == job.location.lower():
            reasons.append(MatchReason(
                feature='location',
                weight=1.0,
                note=f"Location match: {candidate.location}"
            ))
            return 1.0, reasons
        
        # Partial match (e.g., both in same city)
        if any(loc in candidate.location.lower() for loc in ['kl', 'kuala lumpur']) and any(loc in job.location.lower() for loc in ['kl', 'kuala lumpur']):
            reasons.append(MatchReason(
                feature='location',
                weight=0.8,
                note=f"Location partial match: {candidate.location} vs {job.location}"
            ))
            return 0.8, reasons
        
        return 0.0, reasons
