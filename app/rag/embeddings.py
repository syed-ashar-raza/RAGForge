from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import get_settings


@lru_cache
def get_embedder() -> SentenceTransformer:
    return SentenceTransformer(get_settings().embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    model = get_embedder()
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return vectors.tolist()
