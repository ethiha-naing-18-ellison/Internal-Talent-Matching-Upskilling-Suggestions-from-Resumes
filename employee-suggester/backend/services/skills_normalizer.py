import csv
import os
from typing import List, Dict, Set
from pathlib import Path
from ..schemas.common import Skill

class SkillsNormalizer:
    """Normalize skill names using taxonomy mapping."""
    
    def __init__(self, taxonomy_path: str = None):
        if taxonomy_path is None:
            # Default path to skills taxonomy
            taxonomy_path = Path(__file__).resolve().parents[2] / "data" / "taxonomy" / "skills.csv"
        
        self.taxonomy_path = taxonomy_path
        self.canonical_to_aliases: Dict[str, Set[str]] = {}
        self.alias_to_canonical: Dict[str, str] = {}
        self.canonical_weights: Dict[str, float] = {}
        self.canonical_categories: Dict[str, str] = {}
        
        self._load_taxonomy()
    
    def _load_taxonomy(self) -> None:
        """Load skills taxonomy from CSV file."""
        if not os.path.exists(self.taxonomy_path):
            print(f"Warning: Taxonomy file not found at {self.taxonomy_path}")
            return
        
        try:
            with open(self.taxonomy_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    canonical = row.get('canonical', '').strip()
                    if not canonical:
                        continue
                    
                    # Parse aliases - handle both quoted and unquoted formats
                    aliases_str = row.get('aliases', '').strip()
                    if aliases_str.startswith('"') and aliases_str.endswith('"'):
                        aliases_str = aliases_str[1:-1]  # Remove quotes
                    
                    aliases = {alias.strip().lower() for alias in aliases_str.split(',') if alias.strip()}
                    aliases.add(canonical.lower())  # Include canonical name as its own alias
                    
                    # Store mappings
                    self.canonical_to_aliases[canonical.lower()] = aliases
                    for alias in aliases:
                        self.alias_to_canonical[alias] = canonical.lower()
                    
                    # Store metadata
                    self.canonical_weights[canonical.lower()] = 1.0  # Default weight
                    self.canonical_categories[canonical.lower()] = row.get('category', 'unknown')
        
        except Exception as e:
            print(f"Error loading taxonomy: {e}")
    
    def normalize(self, skills: List[str]) -> List[Skill]:
        """
        Normalize a list of skill names to canonical forms.
        
        Args:
            skills: List of skill names (strings)
            
        Returns:
            List of Skill objects with canonical names and default level=2
        """
        normalized_skills = []
        seen_canonicals = set()
        
        for skill_name in skills:
            if not skill_name or not skill_name.strip():
                continue
            
            skill_lower = skill_name.strip().lower()
            
            # Find canonical form
            canonical = self.alias_to_canonical.get(skill_lower, skill_lower)
            
            # Skip if we've already seen this canonical skill
            if canonical in seen_canonicals:
                continue
            
            # Create Skill object
            skill = Skill(
                name=skill_name.strip(),
                canonical=canonical,
                level=2,  # Default level
                last_used=None
            )
            
            normalized_skills.append(skill)
            seen_canonicals.add(canonical)
        
        return normalized_skills
    
    def get_canonical(self, skill_name: str) -> str:
        """Get canonical form of a skill name."""
        skill_lower = skill_name.strip().lower()
        return self.alias_to_canonical.get(skill_lower, skill_lower)
    
    def get_weight(self, canonical_skill: str) -> float:
        """Get weight for a canonical skill."""
        return self.canonical_weights.get(canonical_skill, 1.0)
    
    def get_category(self, canonical_skill: str) -> str:
        """Get category for a canonical skill."""
        return self.canonical_categories.get(canonical_skill, 'unknown')
    
    def is_known_skill(self, skill_name: str) -> bool:
        """Check if a skill name is in our taxonomy."""
        skill_lower = skill_name.strip().lower()
        return skill_lower in self.alias_to_canonical
    
    def get_all_canonical_skills(self) -> List[str]:
        """Get all canonical skill names."""
        return list(self.canonical_to_aliases.keys())
