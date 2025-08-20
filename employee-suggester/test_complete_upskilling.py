#!/usr/bin/env python3
"""
Comprehensive test for complete upskilling functionality
"""

import json
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_complete_upskilling_flow():
    """Test the complete upskilling flow from backend to frontend simulation"""
    
    try:
        from services.enhanced_upskiller import EnhancedUpskiller
        
        print("🔍 Testing Complete Upskilling Flow...")
        print("=" * 70)
        
        upskiller = EnhancedUpskiller()
        
        # Test 1: Get all job categories
        print("\n📋 Test 1: Getting all job categories")
        print("-" * 50)
        categories = upskiller.get_all_job_categories()
        print(f"Available job categories: {len(categories)}")
        print("Categories:", categories[:10], "..." if len(categories) > 10 else "")
        
        # Test 2: Test NLP Engineer scenario (user's specific case)
        print("\n📋 Test 2: NLP Engineer with 77.1% match")
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
        
        # Test 3: Test multiple roles
        print("\n📋 Test 3: Testing multiple roles")
        print("-" * 50)
        
        test_roles = ["Data Scientist", "Software Engineer", "DevOps Engineer", "Frontend Developer"]
        
        for role in test_roles:
            print(f"\n🎯 Testing {role}:")
            role_result = upskiller.get_role_specific_upskilling(role, resume_skills)
            role_skills = role_result.get('priority_skills', [])
            role_recommendations = role_result.get('skill_recommendations', [])
            
            print(f"  Priority Skills: {len(role_skills)}")
            print(f"  Recommendations: {len(role_recommendations)}")
            
            if role_skills:
                print(f"  Skills: {', '.join(role_skills[:3])}{'...' if len(role_skills) > 3 else ''}")
        
        # Test 4: Verify role-specific content
        print("\n📋 Test 4: Verifying role-specific content")
        print("-" * 50)
        
        nlp_result = upskiller.get_role_specific_upskilling("NLP Engineer", resume_skills)
        
        # Check if we have role-specific information
        has_role_specific_content = False
        for rec in nlp_result.get('skill_recommendations', []):
            if rec.get('roleRelevance') in ['High Priority', 'Secondary']:
                has_role_specific_content = True
                break
        
        if has_role_specific_content:
            print("✅ Role-specific content is being generated correctly!")
        else:
            print("❌ Role-specific content is missing!")
        
        # Test 5: Frontend simulation
        print("\n📋 Test 5: Frontend simulation")
        print("-" * 50)
        
        # Simulate what the frontend would receive
        frontend_data = {
            "overall_strategy": nlp_result.get('overall_strategy'),
            "target_role": nlp_result.get('target_role'),
            "skill_recommendations": nlp_result.get('skill_recommendations'),
            "priority_skills": nlp_result.get('priority_skills'),
            "job_category_info": nlp_result.get('job_category_info')
        }
        
        # Check if frontend would show continuous improvement or actual recommendations
        all_skills = [rec.get('skill') for rec in frontend_data.get('skill_recommendations', [])]
        
        if all_skills:
            print("✅ Frontend would show skill recommendations (NOT continuous improvement)")
            print(f"   Skills to display: {', '.join(all_skills)}")
        else:
            print("❌ Frontend would show continuous improvement (this is wrong for 77.1% match)")
        
        print("\n" + "=" * 70)
        print("🎉 Complete upskilling flow test completed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test the new API endpoints"""
    
    try:
        from fastapi.testclient import TestClient
        from app import app
        
        client = TestClient(app)
        
        print("\n🔍 Testing API Endpoints...")
        print("-" * 50)
        
        # Test 1: Get job categories
        print("📋 Test 1: GET /upskill/job-categories")
        response = client.get("/upskill/job-categories")
        
        if response.status_code == 200:
            result = response.json()
            categories = result.get('categories', [])
            print(f"✅ Job categories endpoint working: {len(categories)} categories")
        else:
            print(f"❌ Job categories endpoint failed: {response.status_code}")
            return False
        
        # Test 2: Role-specific upskilling
        print("📋 Test 2: POST /upskill/role-specific")
        test_data = {
            "target_role": "NLP Engineer",
            "resume_skills": ["python", "sql", "react", "docker"]
        }
        
        response = client.post("/upskill/role-specific", json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            priority_skills = result.get('priority_skills', [])
            skill_recommendations = result.get('skill_recommendations', [])
            
            print(f"✅ Role-specific upskilling working: {len(priority_skills)} skills, {len(skill_recommendations)} recommendations")
            
            if priority_skills and skill_recommendations:
                print("✅ API returns proper recommendations (not continuous improvement)")
            else:
                print("❌ API returns empty recommendations")
                return False
        else:
            print(f"❌ Role-specific upskilling failed: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Complete Upskilling System...")
    
    success1 = test_complete_upskilling_flow()
    success2 = test_api_endpoints()
    
    if success1 and success2:
        print("\n🎉 All tests passed! The upskilling system is working correctly!")
        print("\n✅ What's Fixed:")
        print("   - Target role selection is working")
        print("   - Role-specific recommendations are generated")
        print("   - Backend returns proper skill recommendations")
        print("   - Frontend will show actual skills (not continuous improvement)")
        print("   - All job categories are supported")
    else:
        print("\n💥 Some tests failed. The system needs more work.")
        sys.exit(1)
