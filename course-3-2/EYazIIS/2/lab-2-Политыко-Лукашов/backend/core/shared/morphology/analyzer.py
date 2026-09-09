import pymorphy3
from razdel import tokenize
from typing import Any


_CASE_MAP = {
    'nomn': 'именительный',
    'gent': 'родительный',
    'datv': 'дательный',
    'accs': 'винительный',
    'ablt': 'творительный',
    'loct': 'предложный'
}

_NUMBER_MAP = {
    'sing': 'единственное',
    'plur': 'множественное'
}

_GENDER_MAP = {
    'masc': 'мужской',
    'femn': 'женский',
    'neut': 'средний'
}

_POS_MAP = {
    'NOUN': 'существительное',
    'ADJF': 'прилагательное',
    'ADJS': 'прилагательное-краткое',
    'VERB': 'глагол',
    'INFN': 'инфинитив',
    'PRON': 'местоимение',
    'ADV': 'наречие',
    'PREP': 'предлог',
    'CONJ': 'союз',
    'NUM': 'числительное',
    'PRCL': 'частица',
    'PRTF': 'причастие',
    'NPRO': 'местоимение',
    'INTJ': 'междометие',
    'GRND': 'деепричастие',
    'NUMR': 'числительное',
    'ADVB': 'наречие',
    'PRTS': 'краткое причастие',
    'COMP': 'компаратив',
}


def extract_grammemes(tag_grammemes: frozenset) -> dict[str, str]:
    result: dict[str, str] = {}

    for tag, value in _CASE_MAP.items():
        if tag in tag_grammemes:
            result['падеж'] = value
            break

    for tag, value in _NUMBER_MAP.items():
        if tag in tag_grammemes:
            result['число'] = value
            break

    for tag, value in _GENDER_MAP.items():
        if tag in tag_grammemes:
            result['род'] = value
            break

    return result


class MorphAnalyzer:
    def __init__(self):
        self.morph = pymorphy3.MorphAnalyzer()

    def analyze_word(self, word: str) -> dict[str, Any]:
        word_lower = word.lower()
        parses = self.morph.parse(word_lower)
        
        if not parses:
            return {
                'word': word,
                'lemma': word_lower,
                'pos': 'UNKNOWN',
                'grammemes': {}
            }
        
        parse = parses[0]
        
        pos_raw = parse.tag.POS or 'UNKNOWN'
        pos = _POS_MAP.get(pos_raw, pos_raw.lower())
        
        grammemes = extract_grammemes(parse.tag.grammemes)
        
        return {
            'word': word,
            'lemma': parse.normal_form.strip().lower(),
            'pos': pos,
            'grammemes': grammemes,
            'raw_tag': str(parse.tag)
        }

    def analyze_text(self, text: str) -> list[dict[str, Any]]:
        tokens = list(tokenize(text))
        results = []
        
        for token in tokens:
            word = token.text
            if word.isalpha():
                analysis = self.analyze_word(word)
                results.append({
                    'token': word,
                    'position': token.start,
                    'analysis': analysis
                })
        
        return results

    def get_lemma(self, word: str) -> str:
        parses = self.morph.parse(word.lower())
        if parses:
            return parses[0].normal_form.strip().lower()
        return word.lower()

    def get_all_forms(self, word: str) -> list[dict[str, Any]]:
        parses = self.morph.parse(word.lower())
        if not parses:
            return []
        
        parse = parses[0]
        lexeme = getattr(parse, 'lexeme', [])
        
        forms = []
        for form in lexeme[:20]:
            forms.append({
                'word': form.word,
                'grammemes': extract_grammemes(form.tag.grammemes)
            })
        
        return forms
