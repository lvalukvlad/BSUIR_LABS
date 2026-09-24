import io
import re

SUPPORTED_EXTENSIONS = {".txt", ".md", ".csv", ".log", ".html", ".htm", ".rtf", ".pdf", ".docx"}


class UnsupportedFormatError(ValueError):
    pass


def _extract_pdf(data: bytes) -> str:
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(data))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def _strip_html(raw: str) -> str:
    without = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", raw)
    without = re.sub(r"(?s)<[^>]+>", " ", without)
    return re.sub(r"\s+", " ", without).strip()


def extract_text(filename: str, data: bytes) -> str:
    suffix = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if suffix not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFormatError(
            f"Формат {suffix or 'без расширения'} не поддерживается. "
            f"Допустимые: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )
    if suffix == ".pdf":
        return _extract_pdf(data)
    if suffix in {".html", ".htm"}:
        return _strip_html(data.decode("utf-8", errors="ignore"))
    return data.decode("utf-8", errors="ignore").strip()