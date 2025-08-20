#!/usr/bin/env python3
"""
Test script for upskilling functionality
"""

import json
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_upskilling():
    """Test the upskilling functionality"""
    try:
        from services.enhanced_upskiller import EnhancedUpskiller
        
        # Create upskiller instance
        upskiller = EnhancedUpskiller()
        
        # Test data
        resume_skills = ["python", "sql"]
        job_matches = [
            {
                "title": "Data Scientist",
                "score": 0.75,
                "missing_skills": ["machine learning", "aws"]
            }
        ]
        
        # Generate upskilling plan
        result = upskiller.generate_upskilling_plan(
            resume_skills=resume_skills,
            job_matches=job_matches
        )
        
        print("✅ Upskilling test successful!")
        print(f"Target role: {result['target_role']}")
        print(f"Priority skills: {result['priority_skills']}")
        print(f"Overall strategy: {result['overall_strategy']}")
        print(f"Skill recommendations: {len(result['skill_recommendations'])} skills")
        
        return True
        
    except Exception as e:
        print(f"❌ Upskilling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_upskilling()
    sys.exit(0 if success else 1)
