import re
from typing import List, Dict, Any
from pathlib import Path
from ..schemas.common import CandidateProfile, Skill, Role
from ..utils.preprocess import clean_text, extract_skills_from_text, extract_seniority_indicators, estimate_skill_level, parse_date
from .skills_normalizer import SkillsNormalizer

class ResumeParser:
    """Parse resumes and extract structured candidate profiles."""
    
    def __init__(self, taxonomy_path: str = None):
        self.skills_normalizer = SkillsNormalizer(taxonomy_path)
    
    def parse_from_text(self, raw_text: str) -> CandidateProfile:
        """
        Parse resume from raw text.
        
        Args:
            raw_text: Raw resume text
            
        Returns:
            CandidateProfile with extracted information
        """
        if not raw_text or not raw_text.strip():
            return CandidateProfile()
        
        # Use raw text without preprocessing to preserve newlines
        text = raw_text
        # text = clean_text(raw_text)
        
        # Extract basic information
        name = self._extract_name(text)
        location = self._extract_location(text)
        phone = self._extract_phone(text)
        email = self._extract_email(text)
        dept = self._extract_department(text)
        seniority = self._extract_seniority(text)
        
        # Debug logging
        print(f"DEBUG: Raw text: {repr(text)}")
        print(f"DEBUG: Raw text first 5 lines: {text.split('\n')[:5]}")
        print(f"DEBUG: Raw text length: {len(text)}")
        print(f"DEBUG: Raw text contains 'THIHA': {'THIHA' in text}")
        print(f"DEBUG: Raw text contains 'Address:': {'Address:' in text}")
        print(f"DEBUG: Extracted name: '{name}'")
        print(f"DEBUG: Extracted location: '{location}'")
        print(f"DEBUG: Extracted phone: '{phone}'")
        print(f"DEBUG: Extracted email: '{email}'")
        print(f"DEBUG: Extracted dept: '{dept}'")
        
        # Extract skills
        skills = self._extract_skills(text)
        
        # Extract roles/experience
        roles = self._extract_roles(text)
        
        # Extract education
        education = self._extract_education(text)
        
        # Extract certifications
        certs = self._extract_certifications(text)
        
        return CandidateProfile(
            name=name,
            location=location,
            phone=phone,
            email=email,
            dept=dept,
            seniority=seniority,
            skills=skills,
            roles=roles,
            education=education,
            certs=certs
        )
    
    def parse_from_upload(self, file_bytes: bytes, filename: str) -> CandidateProfile:
        """
        Parse resume from uploaded file.
        
        Args:
            file_bytes: File content as bytes
            filename: Original filename
            
        Returns:
            CandidateProfile with extracted information
        """
        # Use existing ingest functionality
        from ..ingest import parse_resume_file
        
        try:
            result = parse_resume_file(file_bytes, filename)
            raw_text = result.get('text', '')
            return self.parse_from_text(raw_text)
        except Exception as e:
            print(f"Error parsing uploaded file: {e}")
            return CandidateProfile()
    
    def _extract_name(self, text: str) -> str:
        """Extract candidate name from resume text."""
        # Simple approach: look for all-caps name at the beginning
        lines = text.split('\n')
        for line in lines[:3]:  # Check first 3 lines
            line = line.strip()
            if not line:
                continue
            
            # Look for all-caps name (2+ words)
            if line.isupper() and len(line.split()) >= 2:
                return line.title()
        
        return ""
    
    def _extract_location(self, text: str) -> str:
        """Extract location from resume text."""
        # Simple approach: find the line that starts with "Address:"
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.lower().startswith('address:'):
                # Extract everything after "Address:"
                address = line.split(':', 1)[1].strip()
                # Remove any trailing parentheses like "(Work)"
                if '(' in address:
                    address = address.split('(')[0].strip()
                return address
        
        return ""
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number from resume text."""
        # Simple approach: find the line that starts with "Phone"
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.lower().startswith('phone'):
                # Extract everything after "Phone number:" or "Phone:"
                if 'phone number:' in line.lower():
                    # Use case-insensitive split
                    parts = re.split(r'phone number:', line, flags=re.IGNORECASE, maxsplit=1)
                    if len(parts) > 1:
                        phone = parts[1].strip()
                    else:
                        continue
                elif 'phone:' in line.lower():
                    # Use case-insensitive split
                    parts = re.split(r'phone:', line, flags=re.IGNORECASE, maxsplit=1)
                    if len(parts) > 1:
                        phone = parts[1].strip()
                    else:
                        continue
                else:
                    continue
                
                # Remove any trailing parentheses like "(Work)"
                if '(' in phone and ')' in phone:
                    # Find the last complete parentheses pair
                    last_open = phone.rfind('(')
                    last_close = phone.rfind(')')
                    if last_open < last_close:
                        # Remove the last parentheses group
                        phone = phone[:last_open].strip()
                
                return phone
        
        return ""
    
    def _extract_email(self, text: str) -> str:
        """Extract email address from resume text."""
        # Look for email patterns
        email_patterns = [
            r'Email\s*(?:address)?:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'  # General email pattern
        ]
        
        for pattern in email_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                email = matches[0].strip()
                return email
        
        return ""
    
    def _extract_department(self, text: str) -> str:
        """Extract department from resume text."""
        # Look for job titles and roles first
        job_title_patterns = [
            r'\b(Data Analyst|Data Scientist|Data Engineer)\b',
            r'\b(Software Engineer|Developer|Programmer)\b',
            r'\b(Product Manager|Project Manager)\b',
            r'\b(DevOps Engineer|System Administrator)\b',
            r'\b(UX Designer|UI Designer|Designer)\b'
        ]
        
        for pattern in job_title_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0]
        
        # Look for department keywords
        dept_patterns = [
            r'\b(IT|Information Technology|Software Engineering)\b',
            r'\b(Data|Analytics|Business Intelligence)\b',
            r'\b(AI|Machine Learning|Data Science)\b',
            r'\b(DevOps|Infrastructure|Platform)\b',
            r'\b(Product|Project Management)\b'
        ]
        
        for pattern in dept_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0]
        
        return ""
    
    def _extract_seniority(self, text: str) -> str:
        """Extract seniority level from resume text."""
        seniority_indicators = extract_seniority_indicators(text)
        
        if any('senior' in indicator.lower() for indicator in seniority_indicators):
            return "Senior"
        elif any('lead' in indicator.lower() for indicator in seniority_indicators):
            return "Lead"
        elif any('principal' in indicator.lower() for indicator in seniority_indicators):
            return "Principal"
        elif any('junior' in indicator.lower() for indicator in seniority_indicators):
            return "Junior"
        else:
            return "Mid-level"
    
    def _extract_skills(self, text: str) -> List[Skill]:
        """Extract and normalize skills from resume text."""
        # Extract potential skills
        potential_skills = extract_skills_from_text(text)
        
        # Normalize skills using taxonomy
        normalized_skills = self.skills_normalizer.normalize(potential_skills)
        
        # Estimate skill levels based on context
        for skill in normalized_skills:
            skill.level = estimate_skill_level(skill.name, text)
        
        return normalized_skills
    
    def _extract_roles(self, text: str) -> List[Role]:
        """Extract work experience roles from resume text."""
        roles = []
        
        # Look for experience sections
        experience_patterns = [
            r'(?i)(experience|work history|employment history)',
            r'(?i)(software engineer|developer|data engineer|analyst)',
            r'(?i)(senior|lead|principal|junior)'
        ]
        
        # Simple extraction: look for job titles with dates
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Look for job title patterns
            if any(title in line.lower() for title in ['engineer', 'developer', 'analyst', 'manager', 'lead']):
                # Try to find dates in nearby lines
                start_date = None
                end_date = None
                
                # Check current and next few lines for dates
                for j in range(i, min(i + 5, len(lines))):
                    date_line = lines[j].strip()
                    dates = re.findall(r'\b(\d{4}-\d{2}|\d{4})\b', date_line)
                    if dates:
                        if not start_date:
                            start_date = dates[0]
                        elif not end_date:
                            end_date = dates[0]
                
                if start_date:
                    role = Role(
                        title=line,
                        start=start_date,
                        end=end_date
                    )
                    roles.append(role)
        
        return roles[:5]  # Limit to 5 most recent roles
    
    def _extract_education(self, text: str) -> List[str]:
        """Extract education information from resume text."""
        education = []
        
        # Look for education section
        education_patterns = [
            r'(?i)(education|academic|degree|bachelor|master|phd)',
            r'(?i)(university|college|institute)'
        ]
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if any(pattern in line.lower() for pattern in education_patterns):
                if line and len(line) > 5:  # Avoid very short lines
                    education.append(line)
        
        return education[:3]  # Limit to 3 education entries
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications from resume text."""
        certs = []
        
        # Look for certification patterns
        cert_patterns = [
            r'(?i)(certification|certified|cert)',
            r'(?i)(aws|azure|gcp|kubernetes|docker)',
            r'(?i)(pmp|scrum|agile)'
        ]
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if any(pattern in line.lower() for pattern in cert_patterns):
                if line and len(line) > 5:  # Avoid very short lines
                    certs.append(line)
        
        return certs[:5]  # Limit to 5 certifications
