from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RAGForge"
    app_env: str = "development"
    log_level: str = "INFO"

    database_url: str = "sqlite:///./data/ragforge.db"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:4b"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    chunk_size: int = 800
    chunk_overlap: int = 120
    top_k: int = 5
    max_context_chars: int = 12000
    max_upload_size_mb: int = 10
    similarity_threshold: float = 0.25

    upload_dir: Path = Path("./data/documents")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def validate_runtime(self):
        if self.chunk_size <= 0:
            raise ValueError("CHUNK_SIZE must be greater than 0")
        if self.chunk_overlap < 0 or self.chunk_overlap >= self.chunk_size:
            raise ValueError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE")
        if self.top_k <= 0:
            raise ValueError("TOP_K must be greater than 0")
        if self.max_upload_size_mb <= 0:
            raise ValueError("MAX_UPLOAD_SIZE_MB must be greater than 0")
        self.upload_dir.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings():
    settings = Settings()
    settings.validate_runtime()
    return settings


settings = get_settings()
