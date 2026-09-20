from app.core.config import Settings


def test_settings_defaults():
    s = Settings()
    assert s.app_name == "RAGForge"
    assert s.chunk_overlap < s.chunk_size
