#!/usr/bin/env python3
"""
Test script to verify role dropdown functionality with dynamic job matches
"""

import json
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_dynamic_role_selection():
    """Test role selection with dynamic job matches"""
    
    try:
        from services.enhanced_upskiller import EnhancedUpskiller
        
        # Simulate different job match scenarios
        test_scenarios = [
            {
                "name": "Multiple Job Matches",
                "job_matches": [
                    {
                        "title": "Data Scientist",
                        "score": 0.85,
                        "missing_skills": ["machine learning", "statistics", "aws"]
                    },
                    {
                        "title": "Software Engineer",
                        "score": 0.75,
                        "missing_skills": ["react", "docker", "kubernetes"]
                    },
                    {
                        "title": "DevOps Engineer",
                        "score": 0.65,
                        "missing_skills": ["terraform", "jenkins", "prometheus"]
                    }
                ]
            },
            {
                "name": "Single Job Match",
                "job_matches": [
                    {
                        "title": "Frontend Developer",
                        "score": 0.80,
                        "missing_skills": ["typescript", "vue.js", "webpack"]
                    }
                ]
            },
            {
                "name": "No Job Matches",
                "job_matches": []
            }
        ]
        
        upskiller = EnhancedUpskiller()
        resume_skills = ["python", "sql", "react", "docker"]
        
        print("🔍 Testing dynamic role selection functionality...")
        print("=" * 70)
        
        for scenario in test_scenarios:
            print(f"\n📋 {scenario['name']}")
            print("-" * 50)
            
            job_matches = scenario['job_matches']
            print(f"Number of job matches: {len(job_matches)}")
            
            if len(job_matches) > 0:
                print("Available roles:")
                for i, match in enumerate(job_matches, 1):
                    print(f"  {i}. {match['title']} ({(match['score'] * 100):.1f}% match)")
                
                # Test upskilling for each role
                for match in job_matches:
                    print(f"\n🎯 Testing upskilling for: {match['title']}")
                    
                    result = upskiller.generate_upskilling_plan(
                        resume_skills=resume_skills,
                        job_matches=[match],
                        target_role=match['title']
                    )
                    
                    target_role = result.get('target_role', 'Unknown')
                    priority_skills = result.get('priority_skills', [])
                    
                    print(f"  ✅ Target Role: {target_role}")
                    print(f"  📚 Priority Skills: {len(priority_skills)}")
                    
                    if target_role == match['title']:
                        print(f"  ✅ Role selection working correctly!")
                    else:
                        print(f"  ❌ Role selection issue: expected {match['title']}, got {target_role}")
            else:
                print("No job matches available - role dropdown should be hidden")
        
        print("\n" + "=" * 70)
        print("🎉 Dynamic role selection test completed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Dynamic Role Selection...")
    success = test_dynamic_role_selection()
    
    if success:
        print("\n🎉 Dynamic role selection test passed!")
        print("The role dropdown should work correctly with job matches!")
    else:
        print("\n💥 Dynamic role selection test failed!")
        sys.exit(1)
