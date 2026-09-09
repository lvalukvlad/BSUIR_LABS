from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class MorphRule:
    ending: str
    grammemes: Dict[str, Any]

    def to_dict(self) -> dict:
        return {
            "ending": self.ending,
            "grammemes": self.grammemes
        }

    @classmethod
    def from_dict(cls, d: dict) -> 'MorphRule':
        return cls(
            ending=d.get('ending', ''),
            grammemes=d.get('grammemes', {})
        )


@dataclass
class LemmaEntry:
    lemma: str
    stem: str
    pos: str
    rules: List[MorphRule] = field(default_factory=list)
    frequency: int = 0
    meta: Optional[dict] = None

    def to_dict(self) -> dict:
        return {
            "lemma": self.lemma,
            "stem": self.stem,
            "pos": self.pos,
            "rules": [r.to_dict() for r in self.rules],
            "frequency": self.frequency,
            "meta": self.meta
        }

    @classmethod
    def from_dict(cls, d: dict) -> 'LemmaEntry':
        rules = [MorphRule.from_dict(r) for r in d.get('rules', [])]
        return cls(
            lemma=d.get('lemma', ''),
            stem=d.get('stem', ''),
            pos=d.get('pos', ''),
            rules=rules,
            frequency=d.get('frequency', 0),
            meta=d.get('meta')
        )