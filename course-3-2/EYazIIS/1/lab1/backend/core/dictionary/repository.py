import json
from pathlib import Path
from typing import Dict, List, Optional
import unicodedata

from .models import LemmaEntry, MorphRule


class DictionaryRepository:
    def __init__(self, path: str = None):
        if path is None:
            backend_dir = Path(__file__).resolve().parent.parent.parent
            self.path = backend_dir / "data" / "dictionary.json"
        else:
            self.path = Path(path)

        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, LemmaEntry] = {}
        self._load_cache()

    def _normalize_key(self, lemma: str) -> str:
        if not lemma:
            return ""
        return unicodedata.normalize('NFC', lemma.strip().lower())

    def _load_cache(self) -> None:
        if not self.path.exists():
            self._cache = {}
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    self._cache = {}
                    return
                data = json.loads(content)
            self._cache = {
                self._normalize_key(item["lemma"]): LemmaEntry.from_dict(item)
                for item in data if isinstance(item, dict) and "lemma" in item
            }
        except Exception as e:
            print(f"Error loading dictionary: {e}")
            self._cache = {}

    def _save_cache(self) -> None:
        try:
            data = [entry.to_dict() for entry in self._cache.values()]
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving dictionary: {e}")

    def get(self, lemma: str) -> Optional[LemmaEntry]:
        key = self._normalize_key(lemma)
        return self._cache.get(key)

    def save(self, entry: LemmaEntry) -> None:
        key = self._normalize_key(entry.lemma)
        entry.lemma = entry.lemma.strip()
        self._cache[key] = entry
        self._save_cache()

    def delete(self, lemma: str) -> bool:
        key = self._normalize_key(lemma)
        if key not in self._cache:
            return False
        del self._cache[key]
        self._save_cache()
        return True

    def search(
        self,
        query: str = "",
        pos_filter: Optional[str] = None,
        min_frequency: Optional[int] = None
    ) -> List[LemmaEntry]:
        entries = list(self._cache.values())

        if query and query.strip():
            q = self._normalize_key(query)
            entries = [e for e in entries if q in self._normalize_key(e.lemma)]

        if pos_filter and pos_filter.strip():
            p = pos_filter.strip().lower()
            entries = [e for e in entries if e.pos.lower() == p]

        if min_frequency is not None:
            entries = [e for e in entries if e.frequency >= min_frequency]

        return sorted(entries, key=lambda x: x.lemma)

    def all(self) -> List[LemmaEntry]:
        return sorted(self._cache.values(), key=lambda x: x.lemma)