#!/usr/bin/env python3
"""
Simple test script for enhanced upskilling functionality
"""

import json
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_enhanced_upskiller():
    """Test the enhanced upskiller directly"""
    
    try:
        from services.enhanced_upskiller import EnhancedUpskiller
        
        # Create upskiller instance
        upskiller = EnhancedUpskiller()
        
        # Test data - similar to what the UI would send
        resume_skills = ["python", "sql"]
        job_matches = [
            {
                "title": "Software Engineer",
                "score": 0.781,
                "missing_skills": ["react", "docker", "aws", "machine learning"]
            },
            {
                "title": "Data Scientist", 
                "score": 0.65,
                "missing_skills": ["machine learning", "aws", "spark"]
            }
        ]
        
        # Generate upskilling plan
        result = upskiller.generate_upskilling_plan(
            resume_skills=resume_skills,
            job_matches=job_matches
        )
        
        print("✅ Enhanced upskiller test successful!")
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
        
        # Verify that we're not getting 0 skills anymore
        if len(result.get('priority_skills', [])) == 0:
            print("❌ Still getting 0 priority skills - this is wrong!")
            return False
        else:
            print(f"✅ Successfully identified {len(result.get('priority_skills', []))} priority skills!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Enhanced Upskiller...")
    success = test_enhanced_upskiller()
    
    if success:
        print("\n🎉 All tests passed! The upskilling system is working correctly.")
        print("The issue with '0 priority skills' has been fixed!")
    else:
        print("\n💥 Tests failed. Please check the implementation.")
        sys.exit(1)
