import chardet
from pathlib import Path
from typing import Any


class TxtParser:
    def parse(self, content: bytes | str) -> str:
        if isinstance(content, str):
            return content
        
        detected = chardet.detect(content)
        encoding = detected['encoding'] or 'utf-8'
        
        try:
            return content.decode(encoding)
        except (UnicodeDecodeError, AttributeError):
            return content.decode('utf-8', errors='ignore')

    def parse_file(self, file_path: Path | str) -> str:
        with open(file_path, 'rb') as f:
            content = f.read()
        return self.parse(content)
