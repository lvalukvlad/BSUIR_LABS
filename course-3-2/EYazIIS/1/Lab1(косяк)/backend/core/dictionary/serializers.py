import json
from typing import List, Dict, Any
from .models import LemmaEntry, MorphRule


class DictionarySerializer:
    @staticmethod
    def serialize_entry(entry: LemmaEntry) -> dict:
        return {
            'lemma': entry.lemma,
            'stem': entry.stem,
            'pos': entry.pos,
            'rules': [
                {
                    'ending': rule.ending,
                    'grammemes': rule.grammemes
                }
                for rule in entry.rules
            ],
            'frequency': entry.frequency,
            'meta': entry.meta
        }

    @staticmethod
    def deserialize_entry(data: dict) -> LemmaEntry:
        rules = [
            MorphRule(
                ending=r['ending'],
                grammemes=r['grammemes']
            )
            for r in data.get('rules', [])
        ]

        return LemmaEntry(
            lemma=data['lemma'],
            stem=data['stem'],
            pos=data['pos'],
            rules=rules,
            frequency=data.get('frequency', 0),
            meta=data.get('meta')
        )

    @staticmethod
    def serialize_list(entries: List[LemmaEntry]) -> list:
        return [DictionarySerializer.serialize_entry(e) for e in entries]

    @staticmethod
    def deserialize_list(data: list) -> List[LemmaEntry]:
        return [DictionarySerializer.deserialize_entry(item) for item in data]

    @staticmethod
    def save_to_json(entries: List[LemmaEntry], path: str):
        data = DictionarySerializer.serialize_list(entries)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load_from_json(path: str) -> List[LemmaEntry]:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return DictionarySerializer.deserialize_list(data)