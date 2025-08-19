#!/usr/bin/env python3
import requests
import json

def test_api():
    url = "http://127.0.0.1:8001/parse_resume_json"
    
    data = {
        "raw_text": "THIHA NAING\nAddress: Jln Tun Razak, Bandar, 05200 Alor Setar, Kedah, Malaysia (Work)\nData Analyst"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Profile: {json.dumps(result, indent=2)}")
            
            profile = result.get('profile', {})
            print(f"Name: '{profile.get('name', '')}'")
            print(f"Location: '{profile.get('location', '')}'")
            print(f"Department: '{profile.get('dept', '')}'")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_api()
