import csv
import re
from pathlib import Path
from typing import Dict, List, Set
from rapidfuzz import process, fuzz

# Simple token pattern (keeps things like C++, .NET, etc.)
WORD = re.compile(r"[A-Za-z0-9\+\#\.][A-Za-z0-9\+\#\.\- ]+")

class SkillTaxonomy:
    """
    Loads a skills CSV with columns: canonical, category, aliases
    Provides normalize(text) -> sorted list of canonical skills found.
    """
    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        self.canonical: Set[str] = set()
        self.alias_to_canon: Dict[str, str] = {}
        self._load()

    def _load(self):
        with self.csv_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                canon = (row.get("canonical") or "").strip()
                if not canon:
                    continue
                self.canonical.add(canon)
                self.alias_to_canon[canon.lower()] = canon
                aliases = [a.strip() for a in (row.get("aliases") or "").split(",") if a.strip()]
                for a in aliases:
                    self.alias_to_canon[a.lower()] = canon

    def normalize(self, text: str) -> List[str]:
        """
        Conservative extractor: word boundary matching to avoid false positives.
        Much fewer false positives for short tokens like R/C.
        """
        import re
        text_low = (text or "").lower()
        found = set()
        for alias_low, canon in self.alias_to_canon.items():
            if not alias_low:
                continue
            # Use word boundary matching for short tokens (≤2 chars) to avoid false positives
            if len(alias_low) <= 2:
                pattern = r'\b' + re.escape(alias_low) + r'\b'
                if re.search(pattern, text_low):
                    found.add(canon)
            else:
                # For longer aliases, keep simple contains matching
                if alias_low in text_low:
                    found.add(canon)
        return sorted(found)
