#!/usr/bin/env python3
"""
Test script for enhanced upskilling functionality
"""

import json
import requests
import sys
from pathlib import Path

def test_enhanced_upskilling_api():
    """Test the enhanced upskilling API endpoint"""
    
    # Test data
    test_data = {
        "resume_skills": ["python", "sql"],
        "job_matches": [
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
    }
    
    try:
        # Make request to the enhanced upskilling API
        response = requests.post(
            "http://127.0.0.1:8002/upskill/enhanced",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Enhanced upskilling API test successful!")
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
            
            return True
            
        else:
            print(f"❌ API request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server. Make sure the server is running on port 8002.")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Enhanced Upskilling API...")
    success = test_enhanced_upskilling_api()
    
    if success:
        print("\n🎉 All tests passed! The upskilling system is working correctly.")
    else:
        print("\n💥 Tests failed. Please check the server and try again.")
        sys.exit(1)
