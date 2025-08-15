from typing import Dict, List
import json, math
from .embed_index import load_index, encode_query

def load_meta(meta_path: str) -> List[Dict]:
    out = []
    with open(meta_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                out.append(json.loads(line))
    return out

def search(index_path: str, meta_path: str, query_text: str, topk: int = 10) -> List[Dict]:
    idx = load_index(index_path)
    # cap k to number of vectors
    k = max(1, min(topk, idx.ntotal))
    q = encode_query(query_text)
    D, I = idx.search(q, k)
    I0, D0 = I[0], D[0]
    meta = load_meta(meta_path)

    results = []
    rank = 1
    for i, score in zip(I0, D0):
        # skip invalids
        if i < 0 or not math.isfinite(float(score)):
            continue
        item = meta[i]
        results.append({"rank": rank, "score": float(score), **item})
        rank += 1
    return results

def score_with_skills(resume_skills: List[str], job_item: Dict, emb_sim: float) -> float:
    must = set(job_item["raw"].get("must_have", []))
    have = set(resume_skills)
    overlap = len(have & must) / max(1, len(must))
    missing = len(must - have)
    return 0.6 * emb_sim + 0.4 * overlap - 0.1 * missing
