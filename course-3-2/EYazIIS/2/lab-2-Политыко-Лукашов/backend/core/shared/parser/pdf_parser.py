from pypdf import PdfReader
from io import BytesIO


class PdfParser:
    def parse(self, content: bytes) -> str:
        pdf = PdfReader(BytesIO(content))
        pages_text = []
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)
        return "\n".join(pages_text)
