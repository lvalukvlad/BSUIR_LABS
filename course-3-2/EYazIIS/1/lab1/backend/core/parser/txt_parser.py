from .base import BaseParser
import chardet


class TxtParser(BaseParser):

    def parse(self, content: bytes) -> str:
        detected = chardet.detect(content)
        encoding = detected['encoding'] or 'utf-8'

        try:
            return content.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            for enc in ['utf-8', 'cp1251', 'koi8-r', 'utf-16']:
                try:
                    return content.decode(enc)
                except:
                    continue
            return content.decode('utf-8', errors='ignore')

    def get_supported_extensions(self) -> list[str]:
        return ['.txt', '.text']