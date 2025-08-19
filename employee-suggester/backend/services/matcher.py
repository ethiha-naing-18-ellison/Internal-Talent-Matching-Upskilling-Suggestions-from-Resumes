from typing import List, Dict, Any
from ..schemas.common import CandidateProfile, JobProfile, JobSkillReq
from ..schemas.match import MatchResult, MatchReason
from ..utils.embeddings import cosine_similarity, text_to_vec
from ..utils.io import load_yaml, get_config_path
import rapidfuzz

class Matcher:
    """Match candidates to jobs based on skills and constraints."""
    
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
        experience_score, experience_reasons = self._score_experience(candidate, job, weights_cfg)
        domain_score, domain_reasons = self._score_domain(candidate, job, weights_cfg)
        location_score, location_reasons = self._score_location(candidate, job, weights_cfg)
        
        # Weighted combination
        weights = weights_cfg.get('weights', {})
        final_score = (
            skills_score * weights.get('skills', 0.55) +
            experience_score * weights.get('experience', 0.25) +
            domain_score * weights.get('domain', 0.15) +
            location_score * weights.get('location', 0.05)
        )
        
        # Combine all reasons
        all_reasons = skills_reasons + experience_reasons + domain_reasons + location_reasons
        
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
