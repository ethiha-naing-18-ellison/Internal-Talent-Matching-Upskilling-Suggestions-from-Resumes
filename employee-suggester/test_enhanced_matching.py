#!/usr/bin/env python3
"""
Test script for enhanced matching functionality (v1.3.0.0)
Tests the new project and education analysis features.
"""

import requests
import json

def test_enhanced_matching():
    """Test the enhanced matching endpoint."""
    
    # Sample resume text with projects and education
    resume_text = """
    SKILLS: Python, SQL, React, Docker, Linux, Machine Learning, Data Analysis
    
    EDUCATION:
    - Bachelor of Computer Science, University of Technology
    - Master of Data Science, Institute of Advanced Studies
    
    PROJECTS:
    - Built a machine learning pipeline for customer churn prediction using Python and scikit-learn
    - Developed a React-based dashboard for real-time data visualization
    - Created ETL pipelines using Apache Airflow and Docker containers
    - Implemented REST APIs using FastAPI and PostgreSQL
    
    EXPERIENCE:
    - Data Engineer at TechCorp (2020-2023)
    - Software Developer at StartupXYZ (2018-2020)
    
    CERTIFICATIONS:
    - AWS Certified Solutions Architect
    - Google Cloud Professional Data Engineer
    """
    
    # Test the enhanced endpoint
    url = "http://127.0.0.1:8001/suggest/roles/v2"
    params = {
        "resume_text": resume_text,
        "topk": 3
    }
    
    try:
        print("Testing enhanced matching endpoint...")
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Enhanced matching successful! Version: {result.get('version', 'unknown')}")
            print(f"Found {len(result['roles'])} matches")
            
            for i, role in enumerate(result['roles'], 1):
                print(f"\n--- Match {i} ---")
                print(f"Role: {role['title']}")
                print(f"Score: {role['score']:.3f}")
                print(f"Matched Skills: {role['matched_skills']}")
                print(f"Missing Skills: {role['missing_skills']}")
                
                if 'enhanced_reasons' in role and role['enhanced_reasons']:
                    print("Enhanced Reasons:")
                    for reason in role['enhanced_reasons']:
                        print(f"  - {reason['feature']}: {reason['note']} (weight: {reason['weight']:.2f})")
                else:
                    print("No enhanced reasons available")
                    
        else:
            print(f"❌ Enhanced endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running on http://127.0.0.1:8001")
    except Exception as e:
        print(f"❌ Error testing enhanced matching: {e}")

def test_backward_compatibility():
    """Test that the original endpoint still works."""
    
    resume_text = "SKILLS: Python, SQL, React"
    
    url = "http://127.0.0.1:8001/suggest/roles"
    params = {
        "resume_text": resume_text,
        "topk": 2
    }
    
    try:
        print("\nTesting backward compatibility...")
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Backward compatibility successful!")
            print(f"Found {len(result['roles'])} matches")
            
            for role in result['roles']:
                print(f"  - {role['title']}: {role['score']:.3f}")
                
        else:
            print(f"❌ Backward compatibility failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing backward compatibility: {e}")

if __name__ == "__main__":
    print("🧪 Testing Employee Suggester v1.3.0.0 Enhanced Matching")
    print("=" * 60)
    
    test_enhanced_matching()
    test_backward_compatibility()
    
    print("\n" + "=" * 60)
    print("✅ Testing complete!")
