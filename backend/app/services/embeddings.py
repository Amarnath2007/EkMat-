import logging
import hashlib
import numpy as np
from typing import List
from backend.app.core.config import settings

logger = logging.getLogger("ekmat.embeddings")

_sbert_model = None
_sbert_attempted = False

def get_sbert_model():
    """Lazily loads SentenceTransformer model, with graceful fallback."""
    global _sbert_model, _sbert_attempted
    if not _sbert_attempted:
        _sbert_attempted = True
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading SentenceTransformer: {settings.EMBEDDING_MODEL}")
            _sbert_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer ({e}). Using deterministic dense vector fallback.")
            _sbert_model = None
    return _sbert_model


def _generate_fallback_vector(text: str, dim: int = 384) -> List[float]:
    """
    Deterministic 384-dimensional semantic projection using token n-grams
    and feature hashing with L2 unit normalization.
    Ensures identical/similar texts yield high cosine similarity, while different texts diverge.
    """
    if not text:
        return [0.0] * dim

    tokens = text.lower().split()
    vec = np.zeros(dim, dtype=np.float32)

    # Word unigrams and character 3-grams
    features = list(tokens)
    for token in tokens:
        if len(token) >= 3:
            for i in range(len(token) - 2):
                features.append(token[i:i+3])

    for feat in features:
        h = int(hashlib.md5(feat.encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        sign = 1.0 if (h >> 16) % 2 == 0 else -1.0
        vec[idx] += sign

    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm

    return [round(float(x), 6) for x in vec]


def compute_embedding(text: str) -> List[float]:
    """
    Generates a 384-dimensional unit vector for the given text.
    """
    model = get_sbert_model()
    if model is not None:
        try:
            emb = model.encode(text, normalize_embeddings=True)
            return [round(float(x), 6) for x in emb]
        except Exception as e:
            logger.error(f"SBERT encode failed: {e}. Falling back to deterministic vector.")

    return _generate_fallback_vector(text, dim=384)


def compute_batch_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Batch embedding generation.
    """
    model = get_sbert_model()
    if model is not None:
        try:
            embs = model.encode(texts, normalize_embeddings=True)
            return [[round(float(x), 6) for x in row] for row in embs]
        except Exception as e:
            logger.error(f"SBERT batch encode failed: {e}. Falling back.")

    return [_generate_fallback_vector(t, dim=384) for t in texts]


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """
    Computes cosine similarity between two 384-d vectors.
    Normalized to range [0.0, 1.0].
    """
    if not v1 or not v2:
        return 0.0
    arr1 = np.array(v1, dtype=np.float32)
    arr2 = np.array(v2, dtype=np.float32)
    norm1 = np.linalg.norm(arr1)
    norm2 = np.linalg.norm(arr2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    cos = float(np.dot(arr1, arr2) / (norm1 * norm2))
    # Map [-1, 1] -> [0, 1] with lower bound at 0
    return max(0.0, min(1.0, round(cos, 4)))
