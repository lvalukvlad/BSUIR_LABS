import pymorphy3 as pymorphy2
from typing import List, Dict, Any
from core.dictionary.models import MorphRule


class RuleBuilder:
    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()

    def build_from_lemma(self, lemma: str) -> List[MorphRule]:
        rules = []
        seen = set()

        for parse in self.morph.parse(lemma):
            ending = self._extract_ending(lemma, parse.word)
            key = (
                ending,
                parse.tag.case,
                parse.tag.number,
                parse.tag.gender,
                parse.tag.tense,
                parse.tag.person
            )

            if key in seen:
                continue
            seen.add(key)
            grammemes = self._extract_grammemes(parse.tag)

            if grammemes:
                rules.append(MorphRule(ending=ending, grammemes=grammemes))

        rules = self._add_fallback_rules(lemma, rules)
        return rules if rules else [MorphRule(ending="", grammemes={})]

    def _extract_ending(self, lemma: str, word: str) -> str:
        if len(word) > len(lemma) and word.startswith(lemma):
            return word[len(lemma):]
        elif len(lemma) > len(word) and lemma.startswith(word):
            return ""
        else:
            min_len = min(len(lemma), len(word))
            i = 0
            while i < min_len and lemma[i] == word[i]:
                i += 1
            return word[i:] if i < len(word) else ""

    def _extract_grammemes(self, tag) -> Dict[str, str]:
        grammemes = {}

        case_map = {
            'nomn': 'именительный', 'gent': 'родительный',
            'datv': 'дательный', 'accs': 'винительный',
            'ablt': 'творительный', 'loct': 'предложный',
            'voct': 'звательный'
        }
        number_map = {'sing': 'ед', 'plur': 'мн'}
        gender_map = {'masc': 'муж', 'femn': 'жен', 'neut': 'ср'}
        tense_map = {'past': 'прошедшее', 'pres': 'настоящее', 'fut': 'будущее'}
        person_map = {'1per': '1', '2per': '2', '3per': '3'}

        if tag.case:
            grammemes['падеж'] = case_map.get(tag.case, tag.case)
        if tag.number:
            grammemes['число'] = number_map.get(tag.number, tag.number)
        if tag.gender:
            grammemes['род'] = gender_map.get(tag.gender, tag.gender)
        if tag.tense:
            grammemes['время'] = tense_map.get(tag.tense, tag.tense)
        if tag.person:
            grammemes['лицо'] = person_map.get(tag.person, tag.person)
        return grammemes

    def _add_fallback_rules(self, lemma: str, rules: List[MorphRule]) -> List[MorphRule]:
        existing_cases = [r.grammemes.get('падеж') for r in rules]
        existing_numbers = [r.grammemes.get('число') for r in rules]

        gender = None
        for r in rules:
            if r.grammemes.get('род'):
                gender = r.grammemes['род']
                break

        if gender and 'sing' in existing_numbers:
            fallback_endings = {
                'муж': {'родительный': 'а', 'дательный': 'у', 'творительный': 'ом', 'предложный': 'е'},
                'жен': {'родительный': 'ы', 'дательный': 'е', 'творительный': 'ой', 'предложный': 'е'},
                'ср': {'родительный': 'а', 'дательный': 'у', 'творительный': 'ом', 'предложный': 'е'}
            }

            for case, ending in fallback_endings.get(gender, {}).items():
                if case not in existing_cases:
                    rules.append(MorphRule(
                        ending=ending,
                        grammemes={'падеж': case, 'число': 'ед', 'род': gender}
                    ))
        return rules