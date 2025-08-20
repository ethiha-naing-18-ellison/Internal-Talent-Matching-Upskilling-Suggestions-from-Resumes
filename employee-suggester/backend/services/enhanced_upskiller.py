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
        
        # Sort by frequency and include ALL missing skills, not just those in database
        priority_skills = []
        for skill, frequency in sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True):
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
        
        # Comprehensive role mapping with multiple keywords
        role_mapping = {
            # Data roles
            'data scientist': 'Data Scientist',
            'data science': 'Data Scientist',
            'ml engineer': 'Machine Learning Engineer',
            'machine learning engineer': 'Machine Learning Engineer',
            'machine learning': 'Machine Learning Engineer',
            'ai engineer': 'Machine Learning Engineer',
            'artificial intelligence': 'Machine Learning Engineer',
            'data engineer': 'Data Engineer',
            'data engineering': 'Data Engineer',
            'etl': 'Data Engineer',
            'data pipeline': 'Data Engineer',
            
            # Software development roles
            'software engineer': 'Software Engineer',
            'software developer': 'Software Engineer',
            'full stack': 'Full Stack Developer',
            'fullstack': 'Full Stack Developer',
            'full-stack': 'Full Stack Developer',
            'backend': 'Backend Developer',
            'backend developer': 'Backend Developer',
            'frontend': 'Frontend Developer',
            'frontend developer': 'Frontend Developer',
            'front-end': 'Frontend Developer',
            'web developer': 'Full Stack Developer',
            'web development': 'Full Stack Developer',
            
            # DevOps and Cloud roles
            'devops': 'DevOps Engineer',
            'devops engineer': 'DevOps Engineer',
            'site reliability': 'DevOps Engineer',
            'sre': 'DevOps Engineer',
            'cloud engineer': 'Cloud Engineer',
            'cloud': 'Cloud Engineer',
            'aws': 'Cloud Engineer',
            'azure': 'Cloud Engineer',
            'gcp': 'Cloud Engineer',
            'infrastructure': 'DevOps Engineer',
            
            # Business roles
            'business analyst': 'Business Analyst',
            'data analyst': 'Business Analyst',
            'analyst': 'Business Analyst',
            'product manager': 'Product Manager',
            'project manager': 'Project Manager',
            
            # Specialized roles
            'mobile': 'Mobile Developer',
            'ios': 'Mobile Developer',
            'android': 'Mobile Developer',
            'game': 'Game Developer',
            'gaming': 'Game Developer',
            'security': 'Security Engineer',
            'cybersecurity': 'Security Engineer',
            'qa': 'QA Engineer',
            'quality assurance': 'QA Engineer',
            'test': 'QA Engineer',
            'testing': 'QA Engineer'
        }
        
        # Try exact matches first
        for keyword, role in role_mapping.items():
            if keyword in job_title:
                return role
        
        # If no exact match, try partial matches with scoring
        role_scores = {}
        for keyword, role in role_mapping.items():
            if any(word in job_title for word in keyword.split()):
                role_scores[role] = role_scores.get(role, 0) + 1
        
        if role_scores:
            # Return the role with the highest score
            best_role = max(role_scores.items(), key=lambda x: x[1])[0]
            return best_role
        
        # If still no match, try to infer from the job title structure
        title_words = job_title.split()
        
        # Check for common patterns
        if any(word in title_words for word in ['scientist', 'science']):
            return 'Data Scientist'
        elif any(word in title_words for word in ['engineer', 'engineering']):
            return 'Software Engineer'
        elif any(word in title_words for word in ['developer', 'development']):
            return 'Software Engineer'
        elif any(word in title_words for word in ['analyst', 'analysis']):
            return 'Business Analyst'
        elif any(word in title_words for word in ['manager', 'management']):
            return 'Project Manager'
        
        # Final fallback - try to extract from the job title itself
        if job_title:
            # Capitalize the job title and use it as is
            capitalized_title = ' '.join(word.capitalize() for word in job_title.split())
            return capitalized_title
        
        return "Software Engineer"  # Default fallback
    
    def _generate_skill_recommendations(self, priority_skills: List[str], target_role: str) -> List[Dict[str, Any]]:
        """Generate detailed recommendations for each priority skill."""
        
        recommendations = []
        
        # Get job category specific data
        job_category_data = self.upskilling_db.get("jobCategories", {}).get(target_role, {})
        priority_skills_for_role = job_category_data.get("prioritySkills", [])
        
        for skill in priority_skills:
            skill_data = self.upskilling_db.get("skills", {}).get(skill)
            
            # If skill is not in database, create default recommendations
            if not skill_data:
                skill_data = self._create_default_skill_data(skill, target_role)
            
            # Determine if this is a priority skill for the target role
            is_priority = skill in priority_skills_for_role
            
            # Get role-specific relevance
            role_relevance = self._calculate_role_relevance(skill, target_role)
            
            # Filter resources and projects based on target role
            role_specific_resources = self._filter_resources_by_role(skill_data.get("resources", []), target_role)
            role_specific_projects = self._filter_projects_by_role(skill_data.get("projects", []), target_role)
            
            recommendation = {
                "skill": skill,
                "type": skill_data.get("type", "Technical Skill"),
                "difficulty": skill_data.get("difficulty", "Intermediate"),
                "timeToLearn": skill_data.get("timeToLearn", "4-6 weeks"),
                "isPriorityForRole": is_priority,
                "resources": role_specific_resources,
                "projects": role_specific_projects,
                "roleRelevance": role_relevance
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _create_default_skill_data(self, skill: str, target_role: str) -> Dict[str, Any]:
        """Create default skill data for skills not in the database."""
        
        # Map common skill patterns to default data
        skill_lower = skill.lower()
        
        # Programming languages
        if any(lang in skill_lower for lang in ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'php', 'ruby', 'swift', 'kotlin']):
            return {
                "type": "Programming Language",
                "difficulty": "Intermediate",
                "timeToLearn": "4-6 weeks",
                "resources": [
                    {
                        "name": f"{skill.title()} Official Documentation",
                        "type": "Documentation",
                        "platform": "Official",
                        "hours": 20,
                        "description": f"Start with the official {skill.title()} documentation and tutorials to understand the fundamentals, syntax, and best practices."
                    },
                    {
                        "name": f"{skill.title()} for Beginners",
                        "type": "Course",
                        "platform": "Udemy/Coursera",
                        "hours": 40,
                        "description": f"Comprehensive beginner course covering {skill.title()} fundamentals, practical examples, and hands-on projects."
                    },
                    {
                        "name": f"{skill.title()} Practice Projects",
                        "type": "Practice",
                        "platform": "GitHub/LeetCode",
                        "hours": 30,
                        "description": f"Practice {skill.title()} through coding challenges, open-source projects, and real-world applications."
                    }
                ],
                "projects": [
                    {
                        "title": f"{skill.title()} Web Application",
                        "description": f"Build a full-stack web application using {skill.title()}. Include user authentication, database integration, and deployment to cloud platforms."
                    },
                    {
                        "title": f"{skill.title()} API Development",
                        "description": f"Create a RESTful API using {skill.title()}. Include CRUD operations, data validation, authentication, and comprehensive testing."
                    },
                    {
                        "title": f"{skill.title()} Data Processing Tool",
                        "description": f"Develop a data processing tool using {skill.title()}. Handle file I/O, data transformation, and generate reports or visualizations."
                    }
                ]
            }
        
        # Frameworks and libraries
        elif any(framework in skill_lower for framework in ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'laravel', 'rails']):
            return {
                "type": "Framework/Library",
                "difficulty": "Intermediate",
                "timeToLearn": "6-8 weeks",
                "resources": [
                    {
                        "name": f"{skill.title()} Official Tutorial",
                        "type": "Tutorial",
                        "platform": "Official",
                        "hours": 25,
                        "description": f"Follow the official {skill.title()} tutorial to understand core concepts, architecture, and best practices."
                    },
                    {
                        "name": f"{skill.title()} Masterclass",
                        "type": "Course",
                        "platform": "Udemy",
                        "hours": 50,
                        "description": f"Comprehensive course covering {skill.title()} advanced features, real-world projects, and deployment strategies."
                    },
                    {
                        "name": f"{skill.title()} Community Resources",
                        "type": "Community",
                        "platform": "GitHub/Stack Overflow",
                        "hours": 20,
                        "description": f"Explore community resources, open-source projects, and Q&A forums for {skill.title()} best practices and troubleshooting."
                    }
                ],
                "projects": [
                    {
                        "title": f"{skill.title()} Portfolio Project",
                        "description": f"Build a comprehensive portfolio project using {skill.title()}. Showcase your skills with modern UI/UX, responsive design, and advanced features."
                    },
                    {
                        "title": f"{skill.title()} E-commerce Platform",
                        "description": f"Create a full-featured e-commerce platform using {skill.title()}. Include product management, shopping cart, payment integration, and admin dashboard."
                    },
                    {
                        "title": f"{skill.title()} Real-time Application",
                        "description": f"Develop a real-time application using {skill.title()}. Implement WebSocket connections, live updates, and collaborative features."
                    }
                ]
            }
        
        # Cloud and DevOps
        elif any(tech in skill_lower for tech in ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ansible']):
            return {
                "type": "Cloud/DevOps",
                "difficulty": "Intermediate",
                "timeToLearn": "4-6 weeks",
                "resources": [
                    {
                        "name": f"{skill.title()} Fundamentals",
                        "type": "Course",
                        "platform": "Official/AWS/Azure/GCP",
                        "hours": 30,
                        "description": f"Learn {skill.title()} fundamentals through official documentation, free courses, and hands-on labs."
                    },
                    {
                        "name": f"{skill.title()} Certification Prep",
                        "type": "Course",
                        "platform": "A Cloud Guru/Pluralsight",
                        "hours": 40,
                        "description": f"Prepare for {skill.title()} certification with comprehensive training covering all exam objectives and practical scenarios."
                    },
                    {
                        "name": f"{skill.title()} Hands-on Labs",
                        "type": "Practice",
                        "platform": "Official Labs",
                        "hours": 25,
                        "description": f"Practice {skill.title()} through official labs, sandbox environments, and real-world scenarios."
                    }
                ],
                "projects": [
                    {
                        "title": f"{skill.title()} Infrastructure as Code",
                        "description": f"Deploy and manage infrastructure using {skill.title()}. Create automated deployment pipelines, monitoring, and disaster recovery solutions."
                    },
                    {
                        "title": f"{skill.title()} Container Orchestration",
                        "description": f"Build containerized applications and deploy them using {skill.title()}. Include load balancing, auto-scaling, and service discovery."
                    },
                    {
                        "title": f"{skill.title()} CI/CD Pipeline",
                        "description": f"Create a complete CI/CD pipeline using {skill.title()}. Include automated testing, code quality checks, and deployment automation."
                    }
                ]
            }
        
        # Database and data
        elif any(db in skill_lower for db in ['sql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch', 'kafka', 'spark']):
            return {
                "type": "Database/Data",
                "difficulty": "Intermediate",
                "timeToLearn": "3-5 weeks",
                "resources": [
                    {
                        "name": f"{skill.title()} Fundamentals",
                        "type": "Course",
                        "platform": "DataCamp/Pluralsight",
                        "hours": 25,
                        "description": f"Learn {skill.title()} fundamentals, data modeling, query optimization, and best practices for data management."
                    },
                    {
                        "name": f"{skill.title()} Advanced Topics",
                        "type": "Course",
                        "platform": "Udemy",
                        "hours": 35,
                        "description": f"Master advanced {skill.title()} concepts including performance tuning, security, backup strategies, and scalability."
                    },
                    {
                        "name": f"{skill.title()} Practice Exercises",
                        "type": "Practice",
                        "platform": "LeetCode/HackerRank",
                        "hours": 20,
                        "description": f"Practice {skill.title()} through coding challenges, database design problems, and optimization exercises."
                    }
                ],
                "projects": [
                    {
                        "title": f"{skill.title()} Database Design",
                        "description": f"Design and implement a comprehensive database using {skill.title()}. Include complex relationships, indexing strategies, and performance optimization."
                    },
                    {
                        "title": f"{skill.title()} Data Pipeline",
                        "description": f"Build a data pipeline using {skill.title()}. Include ETL processes, data transformation, and real-time data processing."
                    },
                    {
                        "title": f"{skill.title()} Analytics Dashboard",
                        "description": f"Create an analytics dashboard using {skill.title()}. Include complex queries, data visualization, and real-time reporting."
                    }
                ]
            }
        
        # Default for other skills
        else:
            return {
                "type": "Technical Skill",
                "difficulty": "Intermediate",
                "timeToLearn": "4-6 weeks",
                "resources": [
                    {
                        "name": f"{skill.title()} Learning Path",
                        "type": "Course",
                        "platform": "Various",
                        "hours": 30,
                        "description": f"Comprehensive learning path for {skill.title()} covering fundamentals, advanced concepts, and practical applications."
                    },
                    {
                        "name": f"{skill.title()} Official Documentation",
                        "type": "Documentation",
                        "platform": "Official",
                        "hours": 20,
                        "description": f"Study the official {skill.title()} documentation to understand core concepts, APIs, and best practices."
                    },
                    {
                        "name": f"{skill.title()} Community Projects",
                        "type": "Practice",
                        "platform": "GitHub",
                        "hours": 25,
                        "description": f"Explore open-source projects and community resources for {skill.title()} to learn from real-world implementations."
                    }
                ],
                "projects": [
                    {
                        "title": f"{skill.title()} Integration Project",
                        "description": f"Integrate {skill.title()} into a larger application or system. Demonstrate practical usage and problem-solving capabilities."
                    },
                    {
                        "title": f"{skill.title()} Proof of Concept",
                        "description": f"Create a proof of concept using {skill.title()}. Showcase your understanding and ability to implement the technology effectively."
                    },
                    {
                        "title": f"{skill.title()} Portfolio Enhancement",
                        "description": f"Enhance your portfolio by incorporating {skill.title()}. Demonstrate continuous learning and skill development."
                    }
                ]
            }
    
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
    
    def _filter_resources_by_role(self, resources: List[Dict[str, Any]], target_role: str) -> List[Dict[str, Any]]:
        """Filter resources based on target role relevance."""
        if not resources:
            return []
        
        # For now, return all resources but mark them with role relevance
        role_specific_resources = []
        for resource in resources:
            resource_copy = resource.copy()
            resource_copy["roleRelevance"] = self._calculate_resource_relevance(resource, target_role)
            role_specific_resources.append(resource_copy)
        
        return role_specific_resources
    
    def _filter_projects_by_role(self, projects: List[Dict[str, Any]], target_role: str) -> List[Dict[str, Any]]:
        """Filter projects based on target role relevance."""
        if not projects:
            return []
        
        # For now, return all projects but mark them with role relevance
        role_specific_projects = []
        for project in projects:
            project_copy = project.copy()
            project_copy["roleRelevance"] = self._calculate_project_relevance(project, target_role)
            role_specific_projects.append(project_copy)
        
        return role_specific_projects
    
    def _calculate_resource_relevance(self, resource: Dict[str, Any], target_role: str) -> str:
        """Calculate how relevant a resource is for the target role."""
        resource_name = resource.get("name", "").lower()
        resource_description = resource.get("description", "").lower()
        
        # Role-specific keywords
        role_keywords = {
            "Data Scientist": ["data", "analysis", "statistics", "machine learning", "python", "sql"],
            "Machine Learning Engineer": ["machine learning", "ai", "deep learning", "tensorflow", "pytorch"],
            "Software Engineer": ["programming", "development", "web", "api", "backend", "frontend"],
            "DevOps Engineer": ["devops", "cloud", "aws", "docker", "kubernetes", "ci/cd"],
            "Frontend Developer": ["frontend", "react", "vue", "javascript", "css", "ui"],
            "Backend Developer": ["backend", "api", "database", "server", "node.js", "python"],
            "Full Stack Developer": ["full stack", "web", "frontend", "backend", "database"],
            "Cloud Engineer": ["cloud", "aws", "azure", "gcp", "infrastructure", "devops"],
            "Business Analyst": ["business", "analysis", "sql", "excel", "reporting", "analytics"],
            "NLP Engineer": ["nlp", "natural language", "text", "language", "machine learning"]
        }
        
        keywords = role_keywords.get(target_role, [])
        relevance_score = 0
        
        for keyword in keywords:
            if keyword in resource_name or keyword in resource_description:
                relevance_score += 1
        
        if relevance_score >= 2:
            return "High Priority"
        elif relevance_score >= 1:
            return "Secondary"
        else:
            return "General"
    
    def _calculate_project_relevance(self, project: Dict[str, Any], target_role: str) -> str:
        """Calculate how relevant a project is for the target role."""
        project_title = project.get("title", "").lower()
        project_description = project.get("description", "").lower()
        
        # Role-specific keywords
        role_keywords = {
            "Data Scientist": ["data", "analysis", "statistics", "machine learning", "python", "sql"],
            "Machine Learning Engineer": ["machine learning", "ai", "deep learning", "tensorflow", "pytorch"],
            "Software Engineer": ["programming", "development", "web", "api", "backend", "frontend"],
            "DevOps Engineer": ["devops", "cloud", "aws", "docker", "kubernetes", "ci/cd"],
            "Frontend Developer": ["frontend", "react", "vue", "javascript", "css", "ui"],
            "Backend Developer": ["backend", "api", "database", "server", "node.js", "python"],
            "Full Stack Developer": ["full stack", "web", "frontend", "backend", "database"],
            "Cloud Engineer": ["cloud", "aws", "azure", "gcp", "infrastructure", "devops"],
            "Business Analyst": ["business", "analysis", "sql", "excel", "reporting", "analytics"],
            "NLP Engineer": ["nlp", "natural language", "text", "language", "machine learning"]
        }
        
        keywords = role_keywords.get(target_role, [])
        relevance_score = 0
        
        for keyword in keywords:
            if keyword in project_title or keyword in project_description:
                relevance_score += 1
        
        if relevance_score >= 2:
            return "High Priority"
        elif relevance_score >= 1:
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
    
    def get_all_job_categories(self) -> List[str]:
        """Get all available job categories from the database."""
        job_categories = self.upskilling_db.get("jobCategories", {})
        return list(job_categories.keys())
    
    def get_job_category_details(self, role_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific job category."""
        job_categories = self.upskilling_db.get("jobCategories", {})
        return job_categories.get(role_name, {})
    
    def get_role_specific_upskilling(self, target_role: str, resume_skills: List[str]) -> Dict[str, Any]:
        """Generate role-specific upskilling plan for a target role."""
        
        # Get job category data
        job_category_data = self.get_job_category_details(target_role)
        
        if not job_category_data:
            # Create default job category data
            job_category_data = self._create_default_job_category(target_role)
        
        # Get priority skills for this role
        priority_skills = job_category_data.get("prioritySkills", [])
        
        # Filter out skills the user already has
        missing_skills = [skill for skill in priority_skills if skill.lower() not in [s.lower() for s in resume_skills]]
        
        # If no missing skills, add some general improvement skills
        if not missing_skills:
            missing_skills = self._get_general_improvement_skills(target_role)
        
        # Generate recommendations for missing skills
        skill_recommendations = []
        for skill in missing_skills[:5]:  # Limit to top 5
            skill_data = self.upskilling_db.get("skills", {}).get(skill)
            if not skill_data:
                skill_data = self._create_default_skill_data(skill, target_role)
            
            # Filter resources and projects by role
            role_specific_resources = self._filter_resources_by_role(skill_data.get("resources", []), target_role)
            role_specific_projects = self._filter_projects_by_role(skill_data.get("projects", []), target_role)
            
            recommendation = {
                "skill": skill,
                "type": skill_data.get("type", "Technical Skill"),
                "difficulty": skill_data.get("difficulty", "Intermediate"),
                "timeToLearn": skill_data.get("timeToLearn", "4-6 weeks"),
                "isPriorityForRole": True,
                "resources": role_specific_resources,
                "projects": role_specific_projects,
                "roleRelevance": "High Priority"
            }
            skill_recommendations.append(recommendation)
        
        # Calculate overall strategy
        overall_strategy = {
            "currentScore": 75.0,  # Default score
            "targetScore": 90.0,   # Target score
            "improvementNeeded": 15.0,
            "totalSkillsToLearn": len(missing_skills),
            "estimatedWeeks": max(1, len(missing_skills) // 2)
        }
        
        return {
            "overall_strategy": overall_strategy,
            "target_role": target_role,
            "skill_recommendations": skill_recommendations,
            "priority_skills": missing_skills,
            "job_category_info": job_category_data
        }
    
    def _create_default_job_category(self, role_name: str) -> Dict[str, Any]:
        """Create default job category data for roles not in the database."""
        
        # Default priority skills for different roles
        role_skills = {
            "Data Scientist": ["python", "sql", "machine learning", "statistics", "pandas", "numpy"],
            "Machine Learning Engineer": ["python", "machine learning", "deep learning", "tensorflow", "pytorch", "mlops"],
            "Software Engineer": ["python", "javascript", "react", "node.js", "docker", "git"],
            "DevOps Engineer": ["docker", "kubernetes", "aws", "terraform", "jenkins", "linux"],
            "Frontend Developer": ["javascript", "react", "vue.js", "html", "css", "typescript"],
            "Backend Developer": ["python", "node.js", "sql", "docker", "api", "database"],
            "Full Stack Developer": ["javascript", "react", "node.js", "sql", "docker", "git"],
            "Cloud Engineer": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform"],
            "Business Analyst": ["sql", "excel", "python", "tableau", "power bi", "statistics"],
            "NLP Engineer": ["python", "natural language processing", "machine learning", "tensorflow", "pytorch", "nlp"]
        }
        
        return {
            "title": role_name,
            "description": f"Comprehensive upskilling plan for {role_name} role",
            "prioritySkills": role_skills.get(role_name, ["python", "sql", "git"]),
            "certifications": [
                {
                    "name": f"{role_name} Certification",
                    "platform": "Industry Standard",
                    "description": f"Professional certification for {role_name} role"
                }
            ],
            "projects": [
                {
                    "name": f"{role_name} Portfolio Project",
                    "description": f"Build a comprehensive project showcasing {role_name} skills",
                    "difficulty": "Intermediate"
                }
            ]
        }
    
    def _get_general_improvement_skills(self, target_role: str) -> List[str]:
        """Get general improvement skills for a role when user has all priority skills."""
        
        general_skills = {
            "Data Scientist": ["advanced statistics", "big data", "data visualization", "experiment design"],
            "Machine Learning Engineer": ["mlops", "model deployment", "distributed computing", "ml infrastructure"],
            "Software Engineer": ["system design", "microservices", "performance optimization", "security"],
            "DevOps Engineer": ["site reliability engineering", "monitoring", "security", "automation"],
            "Frontend Developer": ["performance optimization", "accessibility", "testing", "build tools"],
            "Backend Developer": ["system design", "scalability", "security", "performance"],
            "Full Stack Developer": ["system design", "deployment", "testing", "performance"],
            "Cloud Engineer": ["multi-cloud", "security", "cost optimization", "automation"],
            "Business Analyst": ["advanced analytics", "data storytelling", "stakeholder management", "process improvement"],
            "NLP Engineer": ["advanced nlp", "multilingual models", "nlp infrastructure", "research"]
        }
        
        return general_skills.get(target_role, ["advanced techniques", "best practices", "industry trends"])
    
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
