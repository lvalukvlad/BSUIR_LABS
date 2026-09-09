import re
from typing import List

def tokenize_russian(text: str) -> List[str]:
    cleaned = re.sub(r"[^\w\s\-\'а-яА-ЯёЁ]", " ", text)
    tokens = [t.lower() for t in cleaned.split()]
    return [t for t in tokens if 2 <= len(t) <= 30 and re.search(r"[а-яё]", t)]