#!/usr/bin/env python3
import re

def debug_name_extraction(text):
    print("=== Debug Name Extraction ===")
    lines = text.split('\n')[:10]
    print(f"First 10 lines: {lines}")
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        print(f"Line {i}: '{line}'")
        
        # Test all caps pattern
        if re.match(r'^[A-Z][A-Z\s]+$', line) and len(line.split()) >= 2:
            print(f"  -> Matches all caps pattern: {line}")
            return line.title()
        
        # Test name: pattern
        if 'name:' in line.lower():
            name_part = line.split(':', 1)[1].strip()
            if name_part:
                print(f"  -> Matches name: pattern: {name_part}")
                return name_part.title()
        
        # Test simple name pattern
        if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+$', line):
            print(f"  -> Matches simple name pattern: {line}")
            return line
    
    print("  -> No name found")
    return ""

def debug_location_extraction(text):
    print("=== Debug Location Extraction ===")
    
    # Test address patterns
    address_patterns = [
        r'Address:\s*([^,\n]+(?:,\s*[^,\n]+)*)',
        r'Location:\s*([^,\n]+(?:,\s*[^,\n]+)*)',
        r'([^,\n]+,\s*\d{5}\s*[^,\n]+,\s*[^,\n]+)'
    ]
    
    for i, pattern in enumerate(address_patterns):
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            print(f"  -> Matches address pattern {i}: {matches[0]}")
            return matches[0].strip()
    
    # Test specific address format
    specific_address = re.search(r'([^,\n]+,\s*[^,\n]+,\s*\d{5}\s*[^,\n]+,\s*[^,\n]+,\s*[^,\n]+)', text, re.IGNORECASE)
    if specific_address:
        print(f"  -> Matches specific address: {specific_address.group(1)}")
        return specific_address.group(1).strip()
    
    print("  -> No location found")
    return ""

# Test with the actual text
test_text = """THIHA NAING 
Phone number: (+60) 187799581 (Work) 
Email address: thiha.naing@student.aiu.edu.my 
Address: Jln Tun Razak, Bandar, 05200 Alor Setar, Kedah, Malaysia (Work) 
ABOUT ME 
Data Analyst"""

print("Original text:")
print(test_text)
print()

name = debug_name_extraction(test_text)
print(f"Extracted name: '{name}'")
print()

location = debug_location_extraction(test_text)
print(f"Extracted location: '{location}'")
