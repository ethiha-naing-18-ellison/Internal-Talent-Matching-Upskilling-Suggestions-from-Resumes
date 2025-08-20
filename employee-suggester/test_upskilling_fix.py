#!/usr/bin/env python3
"""
Test script to verify upskilling fix for cases with missing skills
"""

import json
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_upskilling_with_missing_skills():
    """Test upskilling when there are missing skills (should show recommendations, not continuous improvement)"""
    
    try:
        from services.enhanced_upskiller import EnhancedUpskiller
        
        # Test case: NLP Engineer with 77.1% match score and missing skills
        resume_skills = ["python", "sql", "react", "docker"]
        job_matches = [
            {
                "title": "NLP Engineer",
                "score": 0.771,  # 77.1% match
                "missing_skills": ["natural language processing", "tensorflow", "pytorch", "machine learning"]
            }
        ]
        
        print("🔍 Testing upskilling with missing skills (NLP Engineer scenario)...")
        print("=" * 70)
        
        upskiller = EnhancedUpskiller()
        result = upskiller.generate_upskilling_plan(
            resume_skills=resume_skills,
            job_matches=job_matches,
            target_role="NLP Engineer"
        )
        
        print(f"🎯 Target Role: {result.get('target_role', 'Unknown')}")
        print(f"📊 Current Score: {result.get('overall_strategy', {}).get('currentScore', 'N/A')}%")
        print(f"📊 Target Score: {result.get('overall_strategy', {}).get('targetScore', 'N/A')}%")
        print(f"📊 Improvement Needed: {result.get('overall_strategy', {}).get('improvementNeeded', 'N/A')}%")
        
        priority_skills = result.get('priority_skills', [])
        skill_recommendations = result.get('skill_recommendations', [])
        
        print(f"📚 Priority Skills: {len(priority_skills)}")
        print(f"🎯 Skill Recommendations: {len(skill_recommendations)}")
        
        if priority_skills:
            print("✅ Priority Skills Found:")
            for skill in priority_skills:
                print(f"  - {skill}")
        else:
            print("❌ No priority skills found - this is the problem!")
        
        if skill_recommendations:
            print("✅ Skill Recommendations Found:")
            for rec in skill_recommendations:
                skill = rec.get('skill', 'Unknown')
                resources = len(rec.get('resources', []))
                projects = len(rec.get('projects', []))
                print(f"  - {skill}: {resources} resources, {projects} projects")
        else:
            print("❌ No skill recommendations found - this is the problem!")
        
        # Check if we should show continuous improvement or actual recommendations
        if priority_skills and skill_recommendations:
            print("\n✅ SUCCESS: System correctly shows skill recommendations!")
            print("   This should NOT show 'continuous improvement' message.")
            return True
        else:
            print("\n❌ FAILURE: System incorrectly shows 'continuous improvement'!")
            print("   Should show actual skill recommendations for missing skills.")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_api_response():
    """Test the backend API response directly"""
    
    try:
        from fastapi.testclient import TestClient
        from app import app
        
        client = TestClient(app)
        
        # Test data simulating the NLP Engineer scenario
        test_data = {
            "resume_skills": ["python", "sql", "react", "docker"],
            "job_matches": [
                {
                    "title": "NLP Engineer",
                    "score": 0.771,
                    "missing_skills": ["natural language processing", "tensorflow", "pytorch", "machine learning"]
                }
            ],
            "target_role": "NLP Engineer"
        }
        
        print("\n🔍 Testing backend API response...")
        print("-" * 50)
        
        response = client.post("/upskill/enhanced", json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            
            priority_skills = result.get('priority_skills', [])
            skill_recommendations = result.get('skill_recommendations', [])
            
            print(f"✅ API Response Status: {response.status_code}")
            print(f"📚 Priority Skills: {len(priority_skills)}")
            print(f"🎯 Skill Recommendations: {len(skill_recommendations)}")
            
            if priority_skills:
                print("✅ Backend correctly returns priority skills!")
                return True
            else:
                print("❌ Backend incorrectly returns empty priority skills!")
                return False
        else:
            print(f"❌ API failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Upskilling Fix for Missing Skills...")
    
    success1 = test_upskilling_with_missing_skills()
    success2 = test_backend_api_response()
    
    if success1 and success2:
        print("\n🎉 All tests passed! The upskilling system should now show proper recommendations!")
    else:
        print("\n💥 Some tests failed. The issue might still persist.")
        sys.exit(1)
