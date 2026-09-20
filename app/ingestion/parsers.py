from pathlib import Path

from pypdf import PdfReader

SUPPORTED = {".pdf", ".txt", ".md", ".markdown"}


def parse_document(path: Path) -> tuple[str, int | None]:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED:
        raise ValueError(f"Unsupported file type: {suffix}")
    if suffix == ".pdf":
        reader = PdfReader(str(path))
        pages = []
        for i, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if text:
                pages.append(f"[Page {i}]\n{text}")
        return "\n\n".join(pages), len(reader.pages)
    return path.read_text(encoding="utf-8", errors="replace"), None
