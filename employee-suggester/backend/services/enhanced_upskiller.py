import json
from typing import List, Dict, Any, Optional
from pathlib import Path

class EnhancedUpskiller:
    """Enhanced upskilling service that generates personalized recommendations based on job analysis."""
    
    def __init__(self):
        self.upskilling_db = self._load_upskilling_database()
    
    def _load_upskilling_database(self) -> Dict[str, Any]:
        """Load the comprehensive upskilling database."""
        try:
            # Get the path to the upskilling database file
            current_dir = Path(__file__).parent
            db_file = current_dir.parent.parent / "data" / "upskilling" / "upskilling_database.json"
            with open(db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading upskilling database: {e}")
            return {"skills": {}, "jobCategories": {}}
    
    def generate_upskilling_plan(self, 
                                resume_skills: List[str], 
                                job_matches: List[Dict[str, Any]],
                                target_role: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate comprehensive upskilling plan based on resume analysis and job matches.
        
        Args:
            resume_skills: List of skills found in the resume
            job_matches: List of job matches with scores and missing skills
            target_role: Optional target role for focused recommendations
            
        Returns:
            Dict containing upskilling plan with overall strategy and skill-specific recommendations
        """
        
        # Analyze job matches to identify priority skills
        priority_skills = self._analyze_job_requirements(job_matches, resume_skills)
        
        # Determine target role if not specified
        if not target_role:
            target_role = self._determine_target_role(job_matches)
        
        # Generate skill-specific recommendations
        skill_recommendations = self._generate_skill_recommendations(priority_skills, target_role)
        
        # Calculate overall improvement strategy
        overall_strategy = self._calculate_overall_strategy(job_matches, priority_skills)
        
        result = {
            "overall_strategy": overall_strategy,
            "target_role": target_role,
            "skill_recommendations": skill_recommendations,
            "priority_skills": priority_skills
        }
        
        return result
    
    def _analyze_job_requirements(self, job_matches: List[Dict[str, Any]], resume_skills: List[str]) -> List[str]:
        """Analyze job matches to identify priority skills for upskilling."""
        
        # Collect all missing skills from job matches
        missing_skills = []
        skill_frequency = {}
        
        for match in job_matches:
            if 'missing_skills' in match:
                for skill in match['missing_skills']:
                    skill_lower = skill.lower()
                    missing_skills.append(skill_lower)
                    skill_frequency[skill_lower] = skill_frequency.get(skill_lower, 0) + 1
        
        # Sort by frequency and relevance
        priority_skills = []
        for skill, frequency in sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True):
            if skill in self.upskilling_db.get("skills", {}):
                priority_skills.append(skill)
        
        # Limit to top 5 most frequently missing skills
        return priority_skills[:5]
    
    def _determine_target_role(self, job_matches: List[Dict[str, Any]]) -> str:
        """Determine the most suitable target role based on job matches."""
        
        if not job_matches:
            return "Software Engineer"  # Default fallback
        
        # Find the job with the highest score
        best_match = max(job_matches, key=lambda x: x.get('score', 0))
        job_title = best_match.get('title', '').lower()
        
        # Map job titles to categories
        role_mapping = {
            'data scientist': 'Data Scientist',
            'data engineer': 'Data Engineer',
            'software engineer': 'Software Engineer',
            'frontend': 'Frontend Developer',
            'devops': 'DevOps Engineer',
            'machine learning': 'Machine Learning Engineer',
            'business analyst': 'Business Analyst',
            'cloud': 'Cloud Engineer'
        }
        
        for keyword, role in role_mapping.items():
            if keyword in job_title:
                return role
        
        return "Software Engineer"  # Default fallback
    
    def _generate_skill_recommendations(self, priority_skills: List[str], target_role: str) -> List[Dict[str, Any]]:
        """Generate detailed recommendations for each priority skill."""
        
        recommendations = []
        
        for skill in priority_skills:
            skill_data = self.upskilling_db.get("skills", {}).get(skill)
            if not skill_data:
                continue
            
            # Get job category specific recommendations
            job_category_data = self.upskilling_db.get("jobCategories", {}).get(target_role, {})
            
            # Determine if this is a priority skill for the target role
            is_priority = skill in job_category_data.get("prioritySkills", [])
            
            recommendation = {
                "skill": skill,
                "type": skill_data.get("type", "Technical Skill"),
                "difficulty": skill_data.get("difficulty", "Intermediate"),
                "timeToLearn": skill_data.get("timeToLearn", "4-6 weeks"),
                "isPriorityForRole": is_priority,
                "resources": skill_data.get("resources", []),
                "projects": skill_data.get("projects", []),
                "roleRelevance": self._calculate_role_relevance(skill, target_role)
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _calculate_role_relevance(self, skill: str, target_role: str) -> str:
        """Calculate how relevant a skill is for the target role."""
        
        job_category_data = self.upskilling_db.get("jobCategories", {}).get(target_role, {})
        priority_skills = job_category_data.get("prioritySkills", [])
        secondary_skills = job_category_data.get("secondarySkills", [])
        
        if skill in priority_skills:
            return "High Priority"
        elif skill in secondary_skills:
            return "Secondary"
        else:
            return "General"
    
    def _calculate_overall_strategy(self, job_matches: List[Dict[str, Any]], priority_skills: List[str]) -> Dict[str, Any]:
        """Calculate overall improvement strategy."""
        
        if not job_matches:
            return {
                "currentScore": 0,
                "targetScore": 0,
                "improvementNeeded": 0,
                "estimatedWeeks": 0,
                "focusAreas": []
            }
        
        # Calculate current best score
        current_score = max(match.get('score', 0) for match in job_matches)
        
        # Calculate target score (aim for 15% improvement or 95% max)
        target_score = min(0.95, current_score + 0.15)
        improvement_needed = target_score - current_score
        
        # Calculate estimated time based on priority skills
        total_hours = 0
        for skill in priority_skills:
            skill_data = self.upskilling_db.get("skills", {}).get(skill, {})
            time_str = skill_data.get("timeToLearn", "4-6 weeks")
            # Extract weeks from time string (handle ranges like "8-12 weeks")
            if "weeks" in time_str:
                try:
                    # Handle ranges like "8-12 weeks" by taking the average
                    time_parts = time_str.split()[0].split('-')
                    if len(time_parts) == 2:
                        weeks = (int(time_parts[0]) + int(time_parts[1])) // 2
                    else:
                        weeks = int(time_parts[0])
                    total_hours += weeks * 10  # Assume 10 hours per week
                except (ValueError, IndexError):
                    # Fallback to default
                    total_hours += 5 * 10  # 5 weeks default
        
        estimated_weeks = max(1, total_hours // 10)  # Assume 10 hours per week
        
        return {
            "currentScore": round(current_score * 100, 1),
            "targetScore": round(target_score * 100, 1),
            "improvementNeeded": round(improvement_needed * 100, 1),
            "estimatedWeeks": estimated_weeks,
            "focusAreas": priority_skills[:3],  # Top 3 focus areas
            "totalSkillsToLearn": len(priority_skills)
        }
    
    def get_skill_details(self, skill: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific skill."""
        return self.upskilling_db.get("skills", {}).get(skill)
    
    def get_job_category_details(self, role: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific job category."""
        return self.upskilling_db.get("jobCategories", {}).get(role)
    
    def get_related_skills(self, skill: str) -> List[str]:
        """Get related skills for a given skill."""
        skill_data = self.upskilling_db.get("skills", {}).get(skill, {})
        job_categories = skill_data.get("jobCategories", [])
        
        related_skills = set()
        for category in job_categories:
            category_data = self.upskilling_db.get("jobCategories", {}).get(category, {})
            related_skills.update(category_data.get("prioritySkills", []))
            related_skills.update(category_data.get("secondarySkills", []))
        
        # Remove the original skill and return as list
        related_skills.discard(skill)
        return list(related_skills)
