#!/usr/bin/env python3
"""
Test script to verify target role determination for different job titles
"""

import json
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_target_role_determination():
    """Test target role determination with different job titles"""
    
    try:
        from services.enhanced_upskiller import EnhancedUpskiller
        
        # Test cases with different job titles
        test_cases = [
            {
                "title": "Data Scientist",
                "expected_role": "Data Scientist",
                "score": 0.85
            },
            {
                "title": "Machine Learning Engineer",
                "expected_role": "Machine Learning Engineer", 
                "score": 0.78
            },
            {
                "title": "Data Engineer",
                "expected_role": "Data Engineer",
                "score": 0.72
            },
            {
                "title": "Frontend Developer",
                "expected_role": "Frontend Developer",
                "score": 0.68
            },
            {
                "title": "DevOps Engineer",
                "expected_role": "DevOps Engineer",
                "score": 0.65
            },
            {
                "title": "Full Stack Developer",
                "expected_role": "Full Stack Developer",
                "score": 0.75
            },
            {
                "title": "Cloud Engineer",
                "expected_role": "Cloud Engineer",
                "score": 0.70
            },
            {
                "title": "Business Analyst",
                "expected_role": "Business Analyst",
                "score": 0.60
            },
            {
                "title": "Software Engineer",
                "expected_role": "Software Engineer",
                "score": 0.80
            }
        ]
        
        upskiller = EnhancedUpskiller()
        
        print("🔍 Testing target role determination...")
        print("=" * 60)
        
        for i, test_case in enumerate(test_cases, 1):
            job_matches = [{
                "title": test_case["title"],
                "score": test_case["score"],
                "missing_skills": ["python", "sql"]
            }]
            
            # Test the target role determination
            target_role = upskiller._determine_target_role(job_matches)
            expected_role = test_case["expected_role"]
            
            status = "✅" if target_role == expected_role else "❌"
            print(f"{status} Test {i}: '{test_case['title']}' -> '{target_role}' (expected: '{expected_role}')")
            
            if target_role != expected_role:
                print(f"   ⚠️  Mismatch: got '{target_role}', expected '{expected_role}'")
        
        print("=" * 60)
        
        # Test with multiple job matches (should pick the highest scoring one)
        print("\n🔍 Testing with multiple job matches...")
        multiple_matches = [
            {
                "title": "Data Scientist",
                "score": 0.85,
                "missing_skills": ["machine learning", "statistics"]
            },
            {
                "title": "Software Engineer", 
                "score": 0.78,
                "missing_skills": ["react", "docker"]
            },
            {
                "title": "DevOps Engineer",
                "score": 0.65,
                "missing_skills": ["kubernetes", "terraform"]
            }
        ]
        
        target_role = upskiller._determine_target_role(multiple_matches)
        print(f"Multiple matches result: '{target_role}' (should be 'Data Scientist' - highest score)")
        
        if target_role == "Data Scientist":
            print("✅ Correctly identified highest scoring role!")
        else:
            print(f"❌ Expected 'Data Scientist' but got '{target_role}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Target Role Determination...")
    success = test_target_role_determination()
    
    if success:
        print("\n🎉 Target role determination test completed!")
    else:
        print("\n💥 Target role determination test failed!")
        sys.exit(1)
