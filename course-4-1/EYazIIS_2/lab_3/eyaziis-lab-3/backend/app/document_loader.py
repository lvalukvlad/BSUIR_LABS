import io
from pathlib import Path

from pypdf import PdfReader


class UnsupportedFormatError(ValueError):
    pass


def extract_text(filename, data):
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        pdf = PdfReader(io.BytesIO(data))
        parts = []
        for page in pdf.pages:
            parts.append(page.extract_text() or "")
        return "\n".join(parts).strip()
    if ext in {".txt", ".md", ""}:
        for enc in ("utf-8", "cp1251", "latin-1"):
            try:
                return data.decode(enc).strip()
            except UnicodeDecodeError:
                continue
        return data.decode("utf-8", errors="ignore").strip()
    raise UnsupportedFormatError("Нужен txt или pdf")


def split_title(raw):
    lines = raw.splitlines()
    i = None
    for k, line in enumerate(lines):
        if line.strip():
            i = k
            break
    if i is None:
        return "Без названия", raw
    title = lines[i].strip()
    body = "\n".join(lines[i + 1:]).strip()
    return title, body or raw
