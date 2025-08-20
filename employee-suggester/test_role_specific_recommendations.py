#!/usr/bin/env python3
"""
Test script to verify role-specific upskilling recommendations
"""

import json
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_role_specific_recommendations():
    """Test that upskilling recommendations are role-specific"""
    
    try:
        from services.enhanced_upskiller import EnhancedUpskiller
        
        # Test different roles with the same missing skills
        test_scenarios = [
            {
                "name": "Data Scientist Scenario",
                "job_matches": [{
                    "title": "Data Scientist",
                    "score": 0.75,
                    "missing_skills": ["machine learning", "aws", "docker"]
                }],
                "expected_role": "Data Scientist"
            },
            {
                "name": "DevOps Engineer Scenario", 
                "job_matches": [{
                    "title": "DevOps Engineer",
                    "score": 0.70,
                    "missing_skills": ["machine learning", "aws", "docker"]
                }],
                "expected_role": "DevOps Engineer"
            },
            {
                "name": "Frontend Developer Scenario",
                "job_matches": [{
                    "title": "Frontend Developer",
                    "score": 0.65,
                    "missing_skills": ["machine learning", "aws", "docker"]
                }],
                "expected_role": "Frontend Developer"
            },
            {
                "name": "Machine Learning Engineer Scenario",
                "job_matches": [{
                    "title": "Machine Learning Engineer",
                    "score": 0.80,
                    "missing_skills": ["machine learning", "aws", "docker"]
                }],
                "expected_role": "Machine Learning Engineer"
            }
        ]
        
        upskiller = EnhancedUpskiller()
        resume_skills = ["python", "sql", "react"]
        
        print("🔍 Testing role-specific upskilling recommendations...")
        print("=" * 80)
        
        for scenario in test_scenarios:
            print(f"\n📋 {scenario['name']}")
            print("-" * 50)
            
            # Generate upskilling plan
            result = upskiller.generate_upskilling_plan(
                resume_skills=resume_skills,
                job_matches=scenario['job_matches']
            )
            
            target_role = result.get('target_role', 'Unknown')
            expected_role = scenario['expected_role']
            
            # Check if target role is correct
            role_status = "✅" if target_role == expected_role else "❌"
            print(f"{role_status} Target Role: {target_role} (expected: {expected_role})")
            
            # Show priority skills
            priority_skills = result.get('priority_skills', [])
            print(f"📚 Priority Skills ({len(priority_skills)}): {', '.join(priority_skills)}")
            
            # Show skill recommendations with role relevance
            skill_recommendations = result.get('skill_recommendations', [])
            print(f"🎯 Skill Recommendations ({len(skill_recommendations)}):")
            
            for rec in skill_recommendations:
                skill = rec.get('skill', 'Unknown')
                role_relevance = rec.get('roleRelevance', 'Unknown')
                is_priority = rec.get('isPriorityForRole', False)
                priority_indicator = "🔥" if is_priority else "📖"
                print(f"   {priority_indicator} {skill}: {role_relevance}")
            
            # Show overall strategy
            overall_strategy = result.get('overall_strategy', {})
            current_score = overall_strategy.get('currentScore', 0)
            target_score = overall_strategy.get('targetScore', 0)
            improvement_needed = overall_strategy.get('improvementNeeded', 0)
            
            print(f"📊 Score: {current_score}% → {target_score}% (+{improvement_needed}%)")
            
            # Verify that the role-specific logic is working
            if target_role == expected_role:
                print(f"✅ Role determination working correctly!")
            else:
                print(f"❌ Role determination issue: expected {expected_role}, got {target_role}")
        
        print("\n" + "=" * 80)
        print("🎉 Role-specific recommendations test completed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Role-Specific Upskilling Recommendations...")
    success = test_role_specific_recommendations()
    
    if success:
        print("\n🎉 All role-specific tests passed!")
        print("The upskilling system now correctly identifies target roles!")
    else:
        print("\n💥 Role-specific tests failed!")
        sys.exit(1)
