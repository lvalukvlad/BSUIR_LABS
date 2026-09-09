import mammoth
import re
from io import BytesIO


class DocParser:
    def parse(self, content: bytes) -> str:
        result = mammoth.convert_to_text(BytesIO(content))
        return result.value
