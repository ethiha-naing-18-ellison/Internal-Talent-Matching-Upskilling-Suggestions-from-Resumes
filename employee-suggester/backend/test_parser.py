#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.resume_parser import ResumeParser

def test_parsing():
    # Test the improved parsing
    test_text = """THIHA NAING 
Phone number: (+60) 187799581 (Work) 
Email address: thiha.naing@student.aiu.edu.my 
Address: Jln Tun Razak, Bandar, 05200 Alor Setar, Kedah, Malaysia (Work) 
ABOUT ME 
Data Analyst"""

    parser = ResumeParser()
    profile = parser.parse_from_text(test_text)

    print('=== Resume Parsing Test Results ===')
    print('Name:', profile.name)
    print('Location:', profile.location)
    print('Department:', profile.dept)
    print('Seniority:', profile.seniority)
    print('Skills count:', len(profile.skills))
    print('Roles count:', len(profile.roles))
    print('===================================')

if __name__ == "__main__":
    test_parsing()
