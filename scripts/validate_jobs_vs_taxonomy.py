from pathlib import Path
import json, csv, sys

ROOT = Path(__file__).resolve().parents[1]
TAXO = ROOT / "data" / "taxonomy" / "skills.csv"
JOBS = ROOT / "data" / "jobs" / "jobs.jsonl"

def load_taxonomy():
    ok = set()
    with TAXO.open("r", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        for row in rd:
            if row.get("canonical"):
                ok.add(row["canonical"].strip().lower())
    return ok

def load_jobs():
    out = []
    with JOBS.open("r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if line:
                out.append(json.loads(line))
    return out

def main():
    ok = load_taxonomy()
    jobs = load_jobs()
    missing = []
    for j in jobs:
        for k in ("must_have","nice_to_have"):
            for sk in j.get(k, []):
                if sk.strip().lower() not in ok:
                    missing.append((j["id"], j["title"], k, sk))
    if missing:
        print("❌ Missing skills referenced by jobs (add to skills.csv):")
        for m in missing:
            print(f"  {m[0]} {m[1]} | {m[2]} -> {m[3]}")
        sys.exit(1)
    print("✅ All job skills exist in taxonomy.")

if __name__ == "__main__":
    main()
