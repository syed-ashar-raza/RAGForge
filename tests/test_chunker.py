from app.ingestion.chunker import chunk_text, normalize_text


def test_normalize_text():
    assert normalize_text(" a   b\r\n\r\n\r\n c ") == "a b\n\n c"


def test_chunk_overlap_and_reconstruction():
    text = "A " * 1000
    chunks = chunk_text(text, 100, 20)
    assert len(chunks) > 1
    assert all(len(c) <= 100 for c in chunks)


def test_invalid_overlap():
    try:
        chunk_text("abc", 10, 10)
    except ValueError:
        return
    raise AssertionError()
