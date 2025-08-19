#!/usr/bin/env python3
import re

def test_name_extraction(text):
    print("=== Testing Name Extraction ===")
    print(f"Text: {repr(text)}")
    
    # Look for all-caps name pattern in the first part of the text
    first_part = text[:200]
    print(f"First 200 chars: {repr(first_part)}")
    
    name_match = re.search(r'\b([A-Z][A-Z\s]+)\b', first_part)
    if name_match:
        print(f"Found name match: {name_match.group(1)}")
        return name_match.group(1).title()
    else:
        print("No name match found")
        return ""

def test_location_extraction(text):
    print("=== Testing Location Extraction ===")
    print(f"Text: {repr(text)}")
    
    # Simple approach: find the line that starts with "Address:"
    lines = text.split('\n')
    print(f"Lines: {lines}")
    
    for i, line in enumerate(lines):
        line = line.strip()
        print(f"Line {i}: {repr(line)}")
        if line.lower().startswith('address:'):
            # Extract everything after "Address:"
            address = line.split(':', 1)[1].strip()
            # Remove any trailing parentheses like "(Work)"
            if '(' in address:
                address = address.split('(')[0].strip()
            print(f"Found address: {address}")
            return address
    
    print("No address line found")
    return ""

# Test with the actual text
test_text = """THIHA NAING
Phone number: (+60) 187799581 (Work)
Email address: thiha.naing@student.aiu.edu.my
Address: Jln Tun Razak, Bandar, 05200 Alor Setar, Kedah, Malaysia (Work)
ABOUT ME
Data Analyst"""

print("Original test text:")
print(repr(test_text))
print()

name = test_name_extraction(test_text)
print(f"Extracted name: '{name}'")
print()

location = test_location_extraction(test_text)
print(f"Extracted location: '{location}'")
