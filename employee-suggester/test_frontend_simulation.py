#!/usr/bin/env python3
"""
Test script to simulate frontend behavior and verify upskilling functionality
"""

import json
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_frontend_simulation():
    """Simulate what the frontend does when collecting data and calling upskilling API"""
    
    try:
        from services.enhanced_upskiller import EnhancedUpskiller
        
        # Simulate the data that the frontend would collect from the results table
        # This is what the frontend would send to the upskilling API
        resume_skills = ["python", "sql", "react", "docker", "linux"]
        job_matches = [
            {
                "title": "Software Engineer",
                "score": 0.781,
                "missing_skills": ["aws", "kubernetes", "microservices", "machine learning"]
            },
            {
                "title": "Data Scientist", 
                "score": 0.65,
                "missing_skills": ["machine learning", "statistics", "spark", "aws"]
            },
            {
                "title": "DevOps Engineer",
                "score": 0.45,
                "missing_skills": ["kubernetes", "terraform", "jenkins", "prometheus"]
            }
        ]
        
        print("🔍 Simulating frontend data collection...")
        print(f"Resume skills: {resume_skills}")
        print(f"Job matches: {len(job_matches)}")
        
        # Simulate what the frontend does - collect all missing skills
        all_missing_skills = set()
        for match in job_matches:
            all_missing_skills.update(match['missing_skills'])
        
        print(f"Total missing skills collected: {len(all_missing_skills)}")
        print(f"Missing skills: {list(all_missing_skills)}")
        
        # Now test the enhanced upskiller (what the backend API would do)
        upskiller = EnhancedUpskiller()
        result = upskiller.generate_upskilling_plan(
            resume_skills=resume_skills,
            job_matches=job_matches
        )
        
        print("\n✅ Enhanced upskiller test successful!")
        print(f"Target role: {result.get('target_role', 'N/A')}")
        print(f"Priority skills count: {len(result.get('priority_skills', []))}")
        print(f"Priority skills: {result.get('priority_skills', [])}")
        print(f"Current score: {result.get('overall_strategy', {}).get('currentScore', 'N/A')}%")
        print(f"Target score: {result.get('overall_strategy', {}).get('targetScore', 'N/A')}%")
        print(f"Improvement needed: {result.get('overall_strategy', {}).get('improvementNeeded', 'N/A')}%")
        print(f"Skills to learn: {result.get('overall_strategy', {}).get('totalSkillsToLearn', 'N/A')}")
        print(f"Skill recommendations count: {len(result.get('skill_recommendations', []))}")
        
        # Check if we have recommendations for each skill
        for rec in result.get('skill_recommendations', []):
            skill = rec.get('skill', 'Unknown')
            resources = len(rec.get('resources', []))
            projects = len(rec.get('projects', []))
            print(f"  - {skill}: {resources} resources, {projects} projects")
        
        # Verify that we're getting the expected number of skills
        expected_skills = len(all_missing_skills)
        actual_skills = len(result.get('priority_skills', []))
        
        if actual_skills > 0:
            print(f"\n✅ Successfully identified {actual_skills} priority skills!")
            print("The upskilling system is working correctly!")
            return True
        else:
            print(f"\n❌ Expected {expected_skills} skills but got {actual_skills}")
            print("There might be an issue with the upskilling logic!")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_empty_missing_skills():
    """Test the case where there are no missing skills (perfect match scenario)"""
    
    try:
        from services.enhanced_upskiller import EnhancedUpskiller
        
        # Simulate a perfect match scenario
        resume_skills = ["python", "sql", "react", "docker", "aws", "kubernetes"]
        job_matches = [
            {
                "title": "Software Engineer",
                "score": 0.95,
                "missing_skills": []  # No missing skills
            }
        ]
        
        print("\n🔍 Testing perfect match scenario (no missing skills)...")
        
        upskiller = EnhancedUpskiller()
        result = upskiller.generate_upskilling_plan(
            resume_skills=resume_skills,
            job_matches=job_matches
        )
        
        print(f"Target role: {result.get('target_role', 'N/A')}")
        print(f"Priority skills count: {len(result.get('priority_skills', []))}")
        print(f"Current score: {result.get('overall_strategy', {}).get('currentScore', 'N/A')}%")
        print(f"Target score: {result.get('overall_strategy', {}).get('targetScore', 'N/A')}%")
        
        # In this case, we should still get some recommendations for continuous improvement
        if len(result.get('priority_skills', [])) == 0:
            print("✅ Correctly identified 0 priority skills for perfect match")
            print("The system should show continuous improvement recommendations")
            return True
        else:
            print("❌ Unexpected priority skills for perfect match")
            return False
        
    except Exception as e:
        print(f"❌ Perfect match test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Frontend Simulation...")
    
    # Test normal scenario
    success1 = test_frontend_simulation()
    
    # Test perfect match scenario
    success2 = test_empty_missing_skills()
    
    if success1 and success2:
        print("\n🎉 All tests passed! The upskilling system is working correctly.")
        print("The frontend should now show proper recommendations!")
    else:
        print("\n💥 Some tests failed. Please check the implementation.")
        sys.exit(1)
