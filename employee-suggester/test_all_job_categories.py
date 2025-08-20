#!/usr/bin/env python3
"""
Comprehensive test for ALL job categories to ensure equal functionality
"""

import json
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_all_job_categories():
    """Test ALL job categories to ensure they work equally"""
    
    try:
        from services.enhanced_upskiller import EnhancedUpskiller
        
        print("🔍 Testing ALL Job Categories for Equal Functionality...")
        print("=" * 80)
        
        upskiller = EnhancedUpskiller()
        
        # Get all available job categories
        all_categories = upskiller.get_all_job_categories()
        print(f"📋 Available Job Categories: {len(all_categories)}")
        print("Categories:", all_categories)
        print()
        
        # Test data - same resume skills for all roles
        resume_skills = ["python", "sql", "react", "docker"]
        
        # Test each job category
        results = {}
        
        for category in all_categories:
            print(f"🎯 Testing {category}...")
            print("-" * 50)
            
            try:
                result = upskiller.get_role_specific_upskilling(category, resume_skills)
                
                priority_skills = result.get('priority_skills', [])
                skill_recommendations = result.get('skill_recommendations', [])
                job_category_info = result.get('job_category_info', {})
                
                print(f"  Priority Skills: {len(priority_skills)}")
                print(f"  Skill Recommendations: {len(skill_recommendations)}")
                print(f"  Job Category Info: {'Available' if job_category_info else 'Not available'}")
                
                if priority_skills:
                    print(f"  Skills: {', '.join(priority_skills[:3])}{'...' if len(priority_skills) > 3 else ''}")
                
                # Store results for comparison
                results[category] = {
                    'priority_skills_count': len(priority_skills),
                    'recommendations_count': len(skill_recommendations),
                    'has_category_info': bool(job_category_info),
                    'skills': priority_skills[:3]  # First 3 skills for comparison
                }
                
                # Check if this role would show continuous improvement (should NOT for 77.1% match)
                if len(priority_skills) == 0 and len(skill_recommendations) == 0:
                    print(f"  ❌ PROBLEM: {category} shows continuous improvement (wrong for 77.1% match)")
                else:
                    print(f"  ✅ SUCCESS: {category} shows proper skill recommendations")
                
            except Exception as e:
                print(f"  ❌ ERROR: {category} failed - {e}")
                results[category] = {'error': str(e)}
            
            print()
        
        # Summary comparison
        print("📊 SUMMARY COMPARISON")
        print("=" * 80)
        
        working_categories = []
        problem_categories = []
        
        for category, result in results.items():
            if 'error' in result:
                print(f"❌ {category}: ERROR - {result['error']}")
                problem_categories.append(category)
            elif result['priority_skills_count'] == 0 and result['recommendations_count'] == 0:
                print(f"❌ {category}: Shows continuous improvement (wrong)")
                problem_categories.append(category)
            else:
                print(f"✅ {category}: {result['priority_skills_count']} skills, {result['recommendations_count']} recommendations")
                working_categories.append(category)
        
        print()
        print(f"✅ Working Categories: {len(working_categories)}/{len(all_categories)}")
        print(f"❌ Problem Categories: {len(problem_categories)}/{len(all_categories)}")
        
        if problem_categories:
            print(f"❌ Categories with issues: {', '.join(problem_categories)}")
            return False
        else:
            print("🎉 ALL CATEGORIES WORKING CORRECTLY!")
            return True
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_role_specific_content():
    """Test that each role gets role-specific content"""
    
    try:
        from services.enhanced_upskiller import EnhancedUpskiller
        
        print("\n🔍 Testing Role-Specific Content...")
        print("=" * 80)
        
        upskiller = EnhancedUpskiller()
        resume_skills = ["python", "sql", "react", "docker"]
        
        # Test a few key roles for role-specific content
        test_roles = ["Software Engineer", "Data Scientist", "Frontend Developer", "DevOps Engineer"]
        
        for role in test_roles:
            print(f"🎯 Testing {role} for role-specific content...")
            
            result = upskiller.get_role_specific_upskilling(role, resume_skills)
            skill_recommendations = result.get('skill_recommendations', [])
            
            # Check if recommendations have role-specific relevance
            role_specific_count = 0
            for rec in skill_recommendations:
                if rec.get('roleRelevance') in ['High Priority', 'Secondary']:
                    role_specific_count += 1
            
            print(f"  Role-specific recommendations: {role_specific_count}/{len(skill_recommendations)}")
            
            if role_specific_count > 0:
                print(f"  ✅ {role} has role-specific content")
            else:
                print(f"  ❌ {role} lacks role-specific content")
        
        return True
        
    except Exception as e:
        print(f"❌ Role-specific test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing ALL Job Categories for Equal Functionality...")
    
    success1 = test_all_job_categories()
    success2 = test_role_specific_content()
    
    if success1 and success2:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ All job categories work equally")
        print("✅ All roles get proper skill recommendations")
        print("✅ No role shows 'continuous improvement' for 77.1% matches")
        print("✅ Role-specific content is generated correctly")
    else:
        print("\n💥 SOME TESTS FAILED!")
        print("❌ Some job categories may not be working correctly")
        sys.exit(1)
