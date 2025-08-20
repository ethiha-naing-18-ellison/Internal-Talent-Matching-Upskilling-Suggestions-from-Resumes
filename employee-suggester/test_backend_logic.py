#!/usr/bin/env python3
"""
Test script to verify backend logic works correctly
"""

import json
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_backend_logic():
    """Test the backend logic directly"""
    
    try:
        from services.enhanced_upskiller import EnhancedUpskiller
        
        print("🔍 Testing Backend Logic Directly...")
        print("=" * 70)
        
        upskiller = EnhancedUpskiller()
        
        # Test NLP Engineer scenario (user's specific case)
        print("\n📋 Test: NLP Engineer with 77.1% match")
        print("-" * 50)
        
        resume_skills = ["python", "sql", "react", "docker"]
        target_role = "NLP Engineer"
        
        result = upskiller.get_role_specific_upskilling(target_role, resume_skills)
        
        print(f"🎯 Target Role: {result.get('target_role')}")
        print(f"📊 Current Score: {result.get('overall_strategy', {}).get('currentScore')}%")
        print(f"📊 Target Score: {result.get('overall_strategy', {}).get('targetScore')}%")
        print(f"📊 Improvement Needed: {result.get('overall_strategy', {}).get('improvementNeeded')}%")
        
        priority_skills = result.get('priority_skills', [])
        skill_recommendations = result.get('skill_recommendations', [])
        job_category_info = result.get('job_category_info', {})
        
        print(f"📚 Priority Skills: {len(priority_skills)}")
        print(f"🎯 Skill Recommendations: {len(skill_recommendations)}")
        print(f"📋 Job Category Info: {'Available' if job_category_info else 'Not available'}")
        
        if priority_skills:
            print("✅ Priority Skills Found:")
            for skill in priority_skills:
                print(f"  - {skill}")
        
        if skill_recommendations:
            print("✅ Skill Recommendations Found:")
            for rec in skill_recommendations:
                skill = rec.get('skill', 'Unknown')
                resources = len(rec.get('resources', []))
                projects = len(rec.get('projects', []))
                role_relevance = rec.get('roleRelevance', 'Unknown')
                print(f"  - {skill}: {resources} resources, {projects} projects, {role_relevance}")
        
        # Check if this would show continuous improvement or actual recommendations
        all_skills = [rec.get('skill') for rec in skill_recommendations]
        
        if all_skills:
            print("\n✅ SUCCESS: Backend returns proper recommendations!")
            print(f"   Skills to display: {', '.join(all_skills)}")
            print("   This should NOT show 'continuous improvement' message.")
            
            # Save the result for frontend testing
            with open('test_result.json', 'w') as f:
                json.dump(result, f, indent=2)
            print("   Result saved to test_result.json for frontend testing")
            
            return True
        else:
            print("\n❌ FAILURE: Backend returns empty recommendations!")
            print("   This would show 'continuous improvement' message (wrong for 77.1% match)")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Backend Logic...")
    
    success = test_backend_logic()
    
    if success:
        print("\n🎉 Backend logic is working correctly!")
        print("The issue is with the server startup, not the logic itself.")
    else:
        print("\n💥 Backend logic has issues.")
        sys.exit(1)
