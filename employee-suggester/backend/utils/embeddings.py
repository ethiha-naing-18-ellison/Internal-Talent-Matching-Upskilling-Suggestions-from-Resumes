import numpy as np
from typing import List, Optional, Tuple
import hashlib

# Optional imports with graceful fallback
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

def text_to_vec(text: str) -> List[float]:
    """Convert text to vector representation."""
    if SENTENCE_TRANSFORMERS_AVAILABLE:
        return _sentence_transformer_to_vec(text)
    else:
        return _simple_text_to_vec(text)

def _sentence_transformer_to_vec(text: str) -> List[float]:
    """Convert text using sentence transformers."""
    try:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embedding = model.encode(text)
        return embedding.tolist()
    except Exception as e:
        print(f"Sentence transformer failed: {e}")
        return _simple_text_to_vec(text)

def _simple_text_to_vec(text: str) -> List[float]:
    """Simple TF-IDF-like vector representation."""
    # Simple character frequency-based vector
    text_lower = text.lower()
    char_freq = {}
    
    # Count character frequencies
    for char in text_lower:
        if char.isalnum():
            char_freq[char] = char_freq.get(char, 0) + 1
    
    # Create a fixed-size vector (128 dimensions)
    vector = [0.0] * 128
    
    # Fill vector based on character frequencies
    for i, (char, freq) in enumerate(char_freq.items()):
        if i < 128:
            vector[i] = freq / len(text_lower) if text_lower else 0
    
    return vector

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if not vec1 or not vec2:
        return 0.0
    
    # Ensure vectors are same length
    max_len = max(len(vec1), len(vec2))
    vec1_padded = vec1 + [0.0] * (max_len - len(vec1))
    vec2_padded = vec2 + [0.0] * (max_len - len(vec2))
    
    # Convert to numpy arrays
    v1 = np.array(vec1_padded)
    v2 = np.array(vec2_padded)
    
    # Calculate cosine similarity
    dot_product = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))

def build_faiss_index(vectors: List[List[float]], index_path: str) -> bool:
    """Build FAISS index from vectors."""
    if not FAISS_AVAILABLE:
        print("FAISS not available, skipping index building")
        return False
    
    try:
        vectors_array = np.array(vectors, dtype=np.float32)
        dimension = vectors_array.shape[1]
        
        # Create FAISS index
        index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        index.add(vectors_array)
        
        # Save index
        faiss.write_index(index, index_path)
        return True
    except Exception as e:
        print(f"Error building FAISS index: {e}")
        return False

def search_faiss_index(index_path: str, query_vector: List[float], k: int = 10) -> List[Tuple[int, float]]:
    """Search FAISS index."""
    if not FAISS_AVAILABLE:
        print("FAISS not available, returning empty results")
        return []
    
    try:
        # Load index
        index = faiss.read_index(index_path)
        
        # Convert query to numpy array
        query_array = np.array([query_vector], dtype=np.float32)
        
        # Search
        scores, indices = index.search(query_array, k)
        
        # Return results as list of (index, score) tuples
        results = []
        for i in range(len(indices[0])):
            if indices[0][i] != -1:  # FAISS returns -1 for invalid indices
                results.append((int(indices[0][i]), float(scores[0][i])))
        
        return results
    except Exception as e:
        print(f"Error searching FAISS index: {e}")
        return []

def hash_text(text: str) -> str:
    """Hash text for PII redaction."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]
