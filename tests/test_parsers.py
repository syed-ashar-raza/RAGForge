from pathlib import Path

import pytest

from app.ingestion.parsers import parse_document


def test_txt_parser(tmp_path: Path):
    p = tmp_path / "a.txt"
    p.write_text("hello", encoding="utf-8")
    assert parse_document(p) == ("hello", None)


def test_unsupported(tmp_path: Path):
    p = tmp_path / "a.csv"
    p.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError):
        parse_document(p)
