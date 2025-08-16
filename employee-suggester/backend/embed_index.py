import os
from sentence_transformers import SentenceTransformer
from pathlib import Path
import faiss
import numpy as np
import json
from typing import List, Dict, Tuple

MODEL_NAME = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
_MODEL = None

def _get_model():
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(MODEL_NAME)
    return _MODEL

def _normalize(vecs: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-12
    return vecs / norms

def _load_items_jsonl(path: str) -> List[Dict]:
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items

def build_index(items: List[Dict], text_fn, out_dir: str, name: str) -> Tuple[str, str]:
    """
    Build an index for 'items' (jobs or courses).
    - text_fn(item) -> text to embed
    - out_dir: where to save {name}.index and {name}.meta.jsonl
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    model = _get_model()
    texts = [text_fn(it) for it in items]
    emb = model.encode(texts, batch_size=32, show_progress_bar=True)
    emb = _normalize(emb.astype("float32"))

    index = faiss.IndexFlatIP(emb.shape[1])  # Cosine via normalized inner product
    index.add(emb)

    index_path = out / f"{name}.index"
    faiss.write_index(index, str(index_path))

    meta_path = out / f"{name}.meta.jsonl"
    with meta_path.open("w", encoding="utf-8") as f:
        for it, t in zip(items, texts):
            f.write(json.dumps({"id": it.get("id"), "text": t, "raw": it}, ensure_ascii=False) + "\n")

    return str(index_path), str(meta_path)

def load_index(index_path: str):
    return faiss.read_index(index_path)

def encode_query(text: str):
    model = _get_model()
    v = model.encode([text])
    return _normalize(v.astype("float32"))
