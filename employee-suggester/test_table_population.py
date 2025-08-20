#!/usr/bin/env python3
"""
Test script to verify table population logic
"""

import json
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_table_data():
    """Test the data structure that would be used to populate the table"""
    
    # Simulate the data that would come from the backend API
    roles_data = [
        {
            "job_id": "job_001",
            "title": "Software Engineer",
            "score": 0.781,
            "matched_skills": ["python", "sql", "react"],
            "missing_skills": ["aws", "kubernetes", "microservices"],
            "enhanced_reasons": []
        },
        {
            "job_id": "job_002", 
            "title": "Data Scientist",
            "score": 0.65,
            "matched_skills": ["python", "sql"],
            "missing_skills": ["machine learning", "statistics", "spark"],
            "enhanced_reasons": []
        },
        {
            "job_id": "job_003",
            "title": "DevOps Engineer", 
            "score": 0.45,
            "matched_skills": ["docker"],
            "missing_skills": ["kubernetes", "terraform", "jenkins"],
            "enhanced_reasons": []
        }
    ]
    
    print("🔍 Testing table data structure...")
    print(f"Number of roles: {len(roles_data)}")
    
    # Simulate what the frontend would do to collect missing skills
    all_missing_skills = set()
    job_matches = []
    resume_skills = set()
    
    for role in roles_data:
        print(f"\nRole: {role['title']}")
        print(f"  Score: {role['score']}")
        print(f"  Matched skills: {role['matched_skills']}")
        print(f"  Missing skills: {role['missing_skills']}")
        
        # Add to resume skills
        for skill in role['matched_skills']:
            resume_skills.add(skill.lower())
        
        # Add to missing skills
        for skill in role['missing_skills']:
            all_missing_skills.add(skill)
        
        # Add to job matches
        job_matches.append({
            "title": role['title'],
            "score": role['score'],
            "missing_skills": role['missing_skills']
        })
    
    print(f"\n📊 Summary:")
    print(f"Total missing skills: {len(all_missing_skills)}")
    print(f"Missing skills: {list(all_missing_skills)}")
    print(f"Resume skills: {list(resume_skills)}")
    print(f"Job matches: {len(job_matches)}")
    
    # Test the upskilling logic with this data
    try:
        from services.enhanced_upskiller import EnhancedUpskiller
        
        upskiller = EnhancedUpskiller()
        result = upskiller.generate_upskilling_plan(
            resume_skills=list(resume_skills),
            job_matches=job_matches
        )
        
        print(f"\n✅ Upskilling result:")
        print(f"Priority skills: {result.get('priority_skills', [])}")
        print(f"Priority skills count: {len(result.get('priority_skills', []))}")
        print(f"Current score: {result.get('overall_strategy', {}).get('currentScore', 'N/A')}%")
        print(f"Target score: {result.get('overall_strategy', {}).get('targetScore', 'N/A')}%")
        
        if len(result.get('priority_skills', [])) > 0:
            print("✅ Table data is working correctly!")
            return True
        else:
            print("❌ No priority skills found - there's an issue!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing upskilling: {e}")
        return False

if __name__ == "__main__":
    print("Testing Table Population...")
    success = test_table_data()
    
    if success:
        print("\n🎉 Table population test passed!")
        print("The issue might be in the frontend JavaScript logic.")
    else:
        print("\n💥 Table population test failed!")
        sys.exit(1)
