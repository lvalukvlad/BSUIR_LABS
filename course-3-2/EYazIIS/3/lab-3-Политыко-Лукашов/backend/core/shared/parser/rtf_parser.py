from striprtf.striprtf import rtf_to_text


class RtfParser:
    def parse(self, content: bytes | str) -> str:
        if isinstance(content, bytes):
            try:
                content = content.decode('utf-8', errors='ignore')
            except Exception:
                content = content.decode('latin-1', errors='ignore')
        
        return rtf_to_text(content)
