import re
import chardet
from typing import Optional

def detect_encoding(content: bytes) -> str:
    detected = chardet.detect(content)
    return detected['encoding'] or 'utf-8'

def normalize_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s\-\'а-яА-ЯёЁ.,!?;:]', '', text)
    return text.strip()

def extract_words(text: str, min_len: int = 2, max_len: int = 30) -> list[str]:
    cleaned = re.sub(r'[^\w\s\-\'а-яА-ЯёЁ]', ' ', text)
    words = [w.lower() for w in cleaned.split()]
    return [w for w in words if min_len <= len(w) <= max_len and re.search(r'[а-яё]', w)]

def format_frequency(freq: int) -> str:
    if freq >= 1000:
        return f"{freq/1000:.1f}K"
    return str(freq)