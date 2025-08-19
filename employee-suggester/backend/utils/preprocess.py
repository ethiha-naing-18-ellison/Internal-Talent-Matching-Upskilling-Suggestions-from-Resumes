import re
from typing import List, Optional
from datetime import datetime

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\-\/\(\)]', '', text)
    
    return text.strip()

def extract_dates(text: str) -> List[str]:
    """Extract dates in various formats."""
    date_patterns = [
        r'\b(\d{4}-\d{2})\b',  # YYYY-MM
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\b',  # Jan 2024
        r'\b(\d{1,2})/(\d{4})\b',  # MM/YYYY
        r'\b(\d{4})\b'  # YYYY
    ]
    
    dates = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                dates.append(' '.join(match))
            else:
                dates.append(match)
    
    return dates

def parse_date(date_str: str) -> Optional[str]:
    """Parse date string to YYYY-MM format."""
    try:
        # Handle "Jan 2024" format
        if re.match(r'^[A-Za-z]{3}\s+\d{4}$', date_str):
            dt = datetime.strptime(date_str, '%b %Y')
            return dt.strftime('%Y-%m')
        
        # Handle "2024-01" format
        if re.match(r'^\d{4}-\d{2}$', date_str):
            return date_str
        
        # Handle "01/2024" format
        if re.match(r'^\d{1,2}/\d{4}$', date_str):
            dt = datetime.strptime(date_str, '%m/%Y')
            return dt.strftime('%Y-%m')
        
        # Handle "2024" format
        if re.match(r'^\d{4}$', date_str):
            return f"{date_str}-01"
            
    except Exception:
        pass
    
    return None

def extract_skills_from_text(text: str) -> List[str]:
    """Extract potential skills from text."""
    # Common skill patterns
    skill_patterns = [
        r'\b(Python|Java|JavaScript|SQL|React|Angular|Vue|Node\.js|Docker|AWS|Azure|GCP)\b',
        r'\b(Machine Learning|AI|Data Science|DevOps|Agile|Scrum)\b',
        r'\b(HTML|CSS|PHP|Ruby|Go|Rust|C\+\+|C#|\.NET)\b',
        r'\b(Kubernetes|Jenkins|Git|MongoDB|PostgreSQL|MySQL|Redis)\b'
    ]
    
    skills = []
    for pattern in skill_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        skills.extend(matches)
    
    return list(set(skills))

def extract_seniority_indicators(text: str) -> List[str]:
    """Extract seniority indicators from text."""
    seniority_patterns = [
        r'\b(Senior|Lead|Principal|Architect|Manager|Director|VP|CTO|CEO)\b',
        r'\b(Expert|Advanced|Master|Specialist|Consultant)\b',
        r'\b(\d+\+?\s+years?\s+of?\s+experience)\b'
    ]
    
    indicators = []
    for pattern in seniority_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        indicators.extend(matches)
    
    return list(set(indicators))

def estimate_skill_level(skill_name: str, context: str) -> int:
    """Estimate skill level (0-5) based on context."""
    skill_lower = skill_name.lower()
    context_lower = context.lower()
    
    # Level 5 indicators
    if any(word in context_lower for word in ['expert', 'master', 'architect', 'lead']):
        return 5
    
    # Level 4 indicators
    if any(word in context_lower for word in ['senior', 'advanced', 'specialist']):
        return 4
    
    # Level 3 indicators
    if any(word in context_lower for word in ['intermediate', 'mid-level', '3+ years']):
        return 3
    
    # Level 2 indicators
    if any(word in context_lower for word in ['basic', 'beginner', '1+ years']):
        return 2
    
    # Level 1 - just mentioned
    if skill_lower in context_lower:
        return 1
    
    return 0
