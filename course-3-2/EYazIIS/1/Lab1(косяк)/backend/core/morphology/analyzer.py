"""Морфологический анализатор с pymorphy2"""

import pymorphy2
from razdel import tokenize


# Внутренний маппинг (НЕ виден в API!)
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
    """
    Извлекает ТОЛЬКО падеж, род, число из тегов pymorphy2.
    Теги pymorphy2 НЕ видны наружу!
    """
    result = {}

    # Падеж
    for tag, value in _CASE_MAP.items():
        if tag in tag_grammemes:
            result['падеж'] = value
            break

    # Число
    for tag, value in _NUMBER_MAP.items():
        if tag in tag_grammemes:
            result['число'] = value
            break

    # Род
    for tag, value in _GENDER_MAP.items():
        if tag in tag_grammemes:
            result['род'] = value
            break

    return result


class RussianMorphAnalyzer:
    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()

    def analyze_text(self, text: str) -> dict:
        """Анализ текста"""
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
        """
        Построение правил словоизменения.
        Возвращает ТОЛЬКО русские ключи!
        """
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

                # Вычисляем окончание
                word = form.word.lower()
                lemma_lower = lemma.lower()

                common = 0
                for a, b in zip(lemma_lower, word):
                    if a == b:
                        common += 1
                    else:
                        break
                ending = word[common:]

                # Извлекаем ТОЛЬКО падеж, род, число (без тегов!)
                grammemes = _extract_grammemes(form.tag.grammemes)

                if grammemes.get('падеж') or grammemes.get('число'):
                    rules.append({
                        "ending": ending,
                        "grammemes": grammemes
                    })

            # Убираем дубликаты
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