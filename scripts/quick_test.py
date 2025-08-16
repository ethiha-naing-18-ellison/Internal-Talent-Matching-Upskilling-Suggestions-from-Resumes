# End-to-end smoke test:
# - Ingest a sample resume (TXT is fine)
# - Extract normalized skills
# - Retrieve top jobs by embedding similarity
# - Re-score with skill overlap
import sys
from pathlib import Path

# Add the project root to Python path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.ingest import parse_resume_file
from backend.skills import SkillTaxonomy
from backend.retriever import search, score_with_skills
RESUME = ROOT / "data" / "resumes" / "alex.txt"   # change to try others
TAXO   = ROOT / "data" / "taxonomy" / "skills.csv"
MODELS = ROOT / "backend" / "models"

def main():
    content = RESUME.read_bytes()
    parsed = parse_resume_file(content, RESUME.name)

    tax = SkillTaxonomy(str(TAXO))
    skills = tax.normalize(parsed["text"])
    print("== Extracted skills:", skills)

    jobs_index = MODELS / "jobs.index"
    jobs_meta  = MODELS / "jobs.meta.jsonl"

    results = search(str(jobs_index), str(jobs_meta), parsed["text"], topk=10)
    rescored = []
    for r in results:
        s = score_with_skills(skills, r, r["score"])
        rescored.append((s, r))
    rescored.sort(key=lambda x: x[0], reverse=True)

    print("\n== Top job matches (rescored):")
    for s, r in rescored[:5]:
        j = r["raw"]
        must = j.get("must_have", [])
        have = [sk for sk in skills if sk in must]
        miss = [sk for sk in must if sk not in skills]
        print(f"- {j['title']} [{s:.3f}]  have={have}  missing={miss}")

if __name__ == "__main__":
    main()
