#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def extract_name(text):
    """Simple name extraction"""
    lines = text.split('\n')
    for line in lines[:3]:
        line = line.strip()
        if not line:
            continue
        
        # Look for all-caps name (2+ words)
        if line.isupper() and len(line.split()) >= 2:
            return line.title()
    
    return ""

def extract_location(text):
    """Simple location extraction"""
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if line.lower().startswith('address:'):
            address = line.split(':', 1)[1].strip()
            if '(' in address:
                address = address.split('(')[0].strip()
            return address
    
    return ""

# Test
test_text = """THIHA NAING
Address: Jln Tun Razak, Bandar, 05200 Alor Setar, Kedah, Malaysia (Work)
Data Analyst"""

print("Test text:")
print(repr(test_text))
print()

name = extract_name(test_text)
print(f"Name: '{name}'")

location = extract_location(test_text)
print(f"Location: '{location}'")
