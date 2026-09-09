import pymorphy3 as pymorphy2
from razdel import tokenize


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
    'NUM': 'числительное'
}


def _extract_grammemes(tag_grammemes: frozenset) -> dict:
    result = {}

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


class RussianMorphAnalyzer:
    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()

    def analyze_text(self, text: str) -> dict:
        tokens = [t.text.lower() for t in tokenize(text) if t.text.isalpha()]
        lemmas = {}

        for token in tokens:
            try:
                parse = self.morph.parse(token)[0]
                lemma = parse.normal_form

                if lemma not in lemmas:
                    rules = self.build_rules(lemma)
                    lemmas[lemma] = {
                        "lemma": lemma,
                        "stem": lemma,
                        "pos": _POS_MAP.get(parse.tag.POS, parse.tag.POS),
                        "rules": rules,
                        "frequency": 1
                    }
                else:
                    lemmas[lemma]["frequency"] += 1
            except Exception:
                continue

        return lemmas

    def build_rules(self, lemma: str) -> list:
        rules = []
        try:
            parses = self.morph.parse(lemma)
            if not parses:
                return rules

            parse = parses[0]
            lexeme = getattr(parse, 'lexeme', [])

            for form in lexeme[:12]:
                if form.word.lower() == lemma.lower():
                    continue

                word = form.word.lower()
                lemma_lower = lemma.lower()

                common = 0
                for a, b in zip(lemma_lower, word):
                    if a == b:
                        common += 1
                    else:
                        break
                ending = word[common:]

                grammemes = _extract_grammemes(form.tag.grammemes)

                if grammemes.get('падеж') or grammemes.get('число'):
                    rules.append({
                        "ending": ending,
                        "grammemes": grammemes
                    })

            seen = set()
            unique = []
            for r in rules:
                key = (r['ending'], tuple(sorted(r['grammemes'].items())))
                if key not in seen:
                    seen.add(key)
                    unique.append(r)

            return unique[:15]

        except Exception as e:
            print(f"build_rules error: {e}")
            return []
