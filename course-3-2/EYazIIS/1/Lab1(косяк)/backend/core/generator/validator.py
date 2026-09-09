import pymorphy2
from typing import Optional, Tuple
from core.dictionary.models import LemmaEntry, MorphRule


class FormValidator:
    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()

    def validate(self, form: str, expected_lemma: str) -> Tuple[bool, Optional[str]]:
        try:
            parse = self.morph.parse(form)[0]
            actual_lemma = parse.normal_form
            if actual_lemma.lower() == expected_lemma.lower():
                return True, actual_lemma
            else:
                return False, actual_lemma
        except:
            return False, None

    def get_grammemes(self, form: str) -> dict:
        try:
            parse = self.morph.parse(form)[0]
            return {
                'падеж': parse.tag.case,
                'число': parse.tag.number,
                'род': parse.tag.gender,
                'время': parse.tag.tense,
                'лицо': parse.tag.person
            }
        except:
            return {}

    def suggest_correction(self, form: str, expected_grammemes: dict) -> Optional[str]:
        try:
            parse = self.morph.parse(form)[0]
            lemma = parse.normal_form

            for p in self.morph.parse(lemma):
                if self._grammemes_match(p.tag, expected_grammemes):
                    return p.word
        except:
            pass

        return None

    def _grammemes_match(self, tag, expected: dict) -> bool:
        mappings = {
            'падеж': tag.case,
            'число': tag.number,
            'род': tag.gender,
            'время': tag.tense,
            'лицо': tag.person
        }

        for key, expected_value in expected.items():
            actual = mappings.get(key)
            if actual and actual != expected_value:
                return False
        return True