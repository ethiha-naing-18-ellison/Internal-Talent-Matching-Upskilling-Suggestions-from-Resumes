#!/usr/bin/env python3
"""
Simple test script to check API endpoints
"""

import json
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_api_endpoints():
    """Test the API endpoints directly"""
    
    try:
        from app import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test data
        test_resume = "SKILLS: Python, SQL, React, Docker, Linux EXPERIENCE: Built REST APIs and ETL jobs; created dashboards; collaborated with product. PROJECTS: Churn analysis, Next.js dashboard, Airflow pipelines"
        
        print("🔍 Testing /suggest/roles/v2 endpoint...")
        
        # Test the enhanced endpoint
        response = client.get(f"/suggest/roles/v2?resume_text={test_resume}&topk=3")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Enhanced endpoint working!")
            print(f"Found {len(result.get('roles', []))} roles")
            
            for i, role in enumerate(result.get('roles', [])):
                print(f"  Role {i+1}: {role.get('title', 'N/A')}")
                print(f"    Score: {role.get('score', 'N/A')}")
                print(f"    Matched skills: {len(role.get('matched_skills', []))}")
                print(f"    Missing skills: {len(role.get('missing_skills', []))}")
                print(f"    Missing skills list: {role.get('missing_skills', [])}")
                print()
            
            return result
        else:
            print(f"❌ Enhanced endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("Testing API endpoints...")
    result = test_api_endpoints()
    
    if result:
        print("🎉 API test successful!")
    else:
        print("💥 API test failed!")
        sys.exit(1)
