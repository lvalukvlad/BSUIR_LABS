from .base import BaseParser
from striprtf.striprtf import rtf_to_text
import chardet


class RtfParser(BaseParser):
    def parse(self, content: bytes) -> str:
        detected = chardet.detect(content)
        encoding = detected['encoding'] or 'utf-8'
        try:
            text = content.decode(encoding)
        except:
            text = content.decode('utf-8', errors='ignore')
        return rtf_to_text(text)

    def get_supported_extensions(self) -> list[str]:
        return ['.rtf']