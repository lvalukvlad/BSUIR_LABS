from docx import Document
from io import BytesIO


class DocxParser:
    def parse(self, content: bytes) -> str:
        doc = Document(BytesIO(content))
        paragraphs = []
        for par in doc.paragraphs:
            if par.text.strip():
                paragraphs.append(par.text)
        return "\n".join(paragraphs)
