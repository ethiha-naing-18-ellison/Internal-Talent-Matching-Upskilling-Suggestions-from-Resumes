import json
from typing import List, Dict, Any
from pathlib import Path
from ..schemas.upskill import SkillPlan, PlanItem
from ..utils.io import read_jsonl, get_config_path

class UpskillRecommender:
    """Generate upskilling plans for skill gaps."""
    
    def __init__(self):
        self.courses_data = self._load_courses()
    
    def _load_courses(self) -> List[Dict[str, Any]]:
        """Load courses data from JSONL file."""
        try:
            courses_file = get_config_path("../../data/courses/courses.jsonl")
            return read_jsonl(str(courses_file))
        except Exception as e:
            print(f"Error loading courses: {e}")
            return []
    
    def build_upskill_plan(self, gaps: List[str], target_role: str) -> Dict[str, Any]:
        """
        Build upskilling plan for given skill gaps.
        
        Args:
            gaps: List of canonical skill names that need improvement
            target_role: Target role for upskilling
            
        Returns:
            Dict with 'plan' containing list of SkillPlan objects
        """
        skill_plans = []
        
        for skill in gaps:
            # Find courses for this skill
            skill_courses = self._find_courses_for_skill(skill)
            
            if skill_courses:
                # Create learning plan for this skill
                plan_items = []
                total_hours = 0
                
                # Add courses
                for course in skill_courses:
                    plan_items.append(PlanItem(
                        type="course",
                        ref_id=course['id'],
                        label=f"{course['provider']} - {course['level'].title()} {skill.title()}",
                        hours=course['hours'],
                        prereqs=course.get('prereqs', [])
                    ))
                    total_hours += course['hours']
                
                # Add microtasks
                microtasks = self._generate_microtasks(skill, target_role)
                for task in microtasks:
                    plan_items.append(task)
                    total_hours += task.hours
                
                # Calculate ETA (assume 5 hours per week)
                eta_weeks = max(1, (total_hours + 4) // 5)  # Round up
                
                skill_plan = SkillPlan(
                    skill=skill,
                    eta_weeks=eta_weeks,
                    items=plan_items
                )
                
                skill_plans.append(skill_plan)
        
        return {'plan': skill_plans}
    
    def _find_courses_for_skill(self, skill: str) -> List[Dict[str, Any]]:
        """Find courses for a specific skill."""
        skill_lower = skill.lower()
        matching_courses = []
        
        for course in self.courses_data:
            if course.get('skill', '').lower() == skill_lower:
                matching_courses.append(course)
        
        # Sort by level (beginner first) and hours
        matching_courses.sort(key=lambda x: (x.get('level', ''), x.get('hours', 0)))
        
        # Return top 2 courses per skill
        return matching_courses[:2]
    
    def _generate_microtasks(self, skill: str, target_role: str) -> List[PlanItem]:
        """Generate practical microtasks for skill development."""
        microtasks = []
        
        # Skill-specific microtasks
        task_templates = {
            'python': [
                ("Build a simple CLI tool", 4),
                ("Create a REST API with FastAPI", 8),
                ("Write unit tests for existing code", 3),
                ("Refactor legacy code to use modern patterns", 6)
            ],
            'javascript': [
                ("Build a simple web app with vanilla JS", 6),
                ("Create a React component library", 8),
                ("Implement form validation", 3),
                ("Build a simple API with Node.js", 6)
            ],
            'sql': [
                ("Write complex queries for business reports", 4),
                ("Optimize slow queries", 3),
                ("Design a database schema", 5),
                ("Create stored procedures", 4)
            ],
            'docker': [
                ("Containerize an existing application", 4),
                ("Set up multi-stage builds", 3),
                ("Create Docker Compose for local development", 3),
                ("Optimize Docker images", 2)
            ],
            'aws': [
                ("Deploy a simple app to EC2", 4),
                ("Set up S3 bucket with proper permissions", 2),
                ("Create CloudFormation templates", 6),
                ("Configure CloudWatch monitoring", 3)
            ],
            'machine learning': [
                ("Build a simple classification model", 8),
                ("Create a data preprocessing pipeline", 6),
                ("Implement cross-validation", 4),
                ("Deploy a model as a web service", 6)
            ]
        }
        
        skill_lower = skill.lower()
        if skill_lower in task_templates:
            tasks = task_templates[skill_lower]
            for task_name, hours in tasks[:2]:  # Limit to 2 tasks per skill
                microtasks.append(PlanItem(
                    type="microtask",
                    ref_id=f"task-{skill_lower}-{len(microtasks)}",
                    label=task_name,
                    hours=hours,
                    prereqs=[]
                ))
        else:
            # Generic microtasks
            microtasks.append(PlanItem(
                type="microtask",
                ref_id=f"task-{skill_lower}-1",
                label=f"Practice {skill} in a real project",
                hours=6,
                prereqs=[]
            ))
        
        return microtasks
