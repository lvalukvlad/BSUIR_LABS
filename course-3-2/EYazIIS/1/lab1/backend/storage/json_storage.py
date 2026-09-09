import json
from pathlib import Path
from typing import List, Optional, Dict
from .base import BaseStorage
from core.dictionary.models import LemmaEntry, MorphRule
from core.dictionary.serializers import DictionarySerializer


class JsonStorage(BaseStorage):

    def __init__(self, path: str = "data/dictionary.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, entries: List[LemmaEntry]) -> bool:
        try:
            DictionarySerializer.save_to_json(entries, str(self.path))
            return True
        except Exception as e:
            print(f"Error saving dictionary: {e}")
            return False

    def load(self) -> List[LemmaEntry]:
        if not self.path.exists():
            return []
        try:
            return DictionarySerializer.load_from_json(str(self.path))
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def get(self, lemma: str) -> Optional[LemmaEntry]:
        entries = self.load()
        for entry in entries:
            if entry.lemma.lower() == lemma.lower():
                return entry
        return None

    def delete(self, lemma: str) -> bool:
        entries = self.load()
        original_len = len(entries)
        entries = [e for e in entries if e.lemma.lower() != lemma.lower()]

        if len(entries) < original_len:
            self.save(entries)
            return True
        return False

    def search(self, query: str, filters: Optional[Dict] = None) -> List[LemmaEntry]:
        entries = self.load()

        if query:
            entries = [e for e in entries if query.lower() in e.lemma.lower()]

        if filters:
            if 'pos' in filters:
                entries = [e for e in entries if e.pos.lower() == filters['pos'].lower()]
            if 'min_frequency' in filters:
                entries = [e for e in entries if e.frequency >= filters['min_frequency']]

        return sorted(entries, key=lambda x: x.lemma)

    def save_entry(self, entry: LemmaEntry) -> bool:
        entries = {e.lemma: e for e in self.load()}
        entries[entry.lemma] = entry
        return self.save(list(entries.values()))