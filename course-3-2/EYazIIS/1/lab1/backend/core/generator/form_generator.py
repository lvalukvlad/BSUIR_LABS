from typing import Optional, Tuple, Dict
from pymorphy3 import MorphAnalyzer
from core.dictionary.models import LemmaEntry, MorphRule


class WordFormGenerator:

    _morph = MorphAnalyzer()

    @staticmethod
    def _fix_stem(entry: LemmaEntry) -> str:
        lemma = entry.lemma.lower()
        current_stem = entry.stem.lower() if entry.stem else lemma

        if current_stem == lemma:
            try:
                parses = WordFormGenerator._morph.parse(lemma)
                if parses:
                    parse = parses[0]
                    lexeme = getattr(parse, 'lexeme', [])
                    
                    for form in lexeme[:10]:
                        word = form.word.lower()
                        if word != lemma and len(word) > len(lemma):
                            common = 0
                            for a, b in zip(lemma, word):
                                if a == b:
                                    common += 1
                                else:
                                    break
                            if common > 0:
                                new_stem = lemma[:common]
                                if len(new_stem) > 0:
                                    return new_stem
            except Exception:
                pass
        
        return current_stem

    GRAMMEME_MAP = {
        'падеж': {
            'именительный': 'nomn',
            'родительный': 'gent',
            'дательный': 'datv',
            'винительный': 'accs',
            'творительный': 'ablt',
            'предложный': 'loct',
            'звательный': 'voct',
        },
        'число': {
            'ед': 'sing',
            'мн': 'plur',
        },
        'род': {
            'муж': 'masc',
            'жен': 'femn',
            'ср': 'neut',
        },
        'время': {
            'прошедшее': 'past',
            'настоящее': 'pres',
            'будущее': 'futr',
        },
        'лицо': {
            '1': '1per',
            '2': '2per',
            '3': '3per',
        }
    }

    @staticmethod
    def generate(
        entry: LemmaEntry,
        grammemes: Dict[str, str]
    ) -> Tuple[Optional[str], Optional[MorphRule]]:

        target = WordFormGenerator.normalize_grammemes(grammemes)

        form = WordFormGenerator._generate_with_pymorphy(
            entry.lemma,
            entry.pos,
            target
        )

        if form:
            return form, None

        stem = WordFormGenerator._fix_stem(entry)

        for rule in entry.rules:
            rule_grammemes = WordFormGenerator.normalize_grammemes(rule.grammemes)

            if all(rule_grammemes.get(k) == v for k, v in target.items()):
                return stem + rule.ending, rule

        fallback = WordFormGenerator._fallback_noun(entry, target, stem)
        if fallback:
            return fallback, None

        return entry.lemma, None

    @staticmethod
    def _generate_with_pymorphy(
        lemma: str,
        pos: str,
        target: Dict[str, str]
    ) -> Optional[str]:

        morph = WordFormGenerator._morph
        parses = morph.parse(lemma)

        if not parses:
            return None

        grammeme_set = set(target.values())

        for parse in parses:

            if parse.normal_form != lemma.lower():
                continue

            if not WordFormGenerator._pos_matches(parse.tag.POS, pos):
                continue

            cleaned = WordFormGenerator._clean_grammemes(
                grammeme_set,
                parse.tag.POS
            )

            try:
                form = parse.inflect(cleaned)
                if form:
                    return form.word
            except Exception:
                continue

        return None

    @staticmethod
    def _clean_grammemes(grammemes: set, pos: str) -> set:

        cleaned = set(grammemes)

        if 'plur' in cleaned:
            cleaned -= {'masc', 'femn', 'neut'}

        if pos == 'NOUN':
            cleaned -= {'1per', '2per', '3per', 'past', 'pres', 'futr'}

        if pos in {'ADJF', 'ADJS'}:
            cleaned -= {'1per', '2per', '3per'}

        if pos in {'VERB', 'INFN'}:
            cleaned -= {'nomn', 'gent', 'datv', 'accs', 'ablt', 'loct'}

        return cleaned

    @staticmethod
    def _pos_matches(parse_pos: str, entry_pos: str) -> bool:

        entry_pos = entry_pos.lower()

        mapping = {
            'существительное': 'NOUN',
            'noun': 'NOUN',
            'прилагательное': 'ADJF',
            'adj': 'ADJF',
            'глагол': 'VERB',
            'verb': 'VERB',
        }

        expected = mapping.get(entry_pos)

        if not expected:
            return True

        if expected == 'VERB':
            return parse_pos in {'VERB', 'INFN'}

        return parse_pos == expected


    @staticmethod
    def _fallback_noun(
        entry: LemmaEntry,
        target: Dict[str, str],
        stem: str = None
    ) -> Optional[str]:

        if entry.pos.lower() not in ['существительное', 'noun']:
            return None

        if stem is None:
            stem = WordFormGenerator._extract_noun_stem(entry.lemma)

        number = target.get('число', 'sing')
        case = target.get('падеж', 'nomn')

        endings = {
            'sing': {
                'nomn': '',
                'gent': 'а',
                'datv': 'у',
                'accs': '',
                'ablt': 'ом',
                'loct': 'е'
            },
            'plur': {
                'nomn': 'ы',
                'gent': 'ов',
                'datv': 'ам',
                'accs': 'ы',
                'ablt': 'ами',
                'loct': 'ах'
            }
        }

        ending = endings.get(number, {}).get(case)
        if ending is None:
            return None

        return stem + ending


    @staticmethod
    def _extract_noun_stem(lemma: str) -> str:

        lemma = lemma.lower()

        if lemma.endswith(('а', 'я', 'о', 'е')):
            return lemma[:-1]

        return lemma


    @staticmethod
    def normalize_grammemes(
        grammemes: Dict[str, str]
    ) -> Dict[str, str]:

        result = {}

        for key, value in grammemes.items():
            if key in WordFormGenerator.GRAMMEME_MAP:
                mapped = WordFormGenerator.GRAMMEME_MAP[key].get(value, value)
                result[key] = mapped
            else:
                result[key] = value

        return result


    @staticmethod
    def validate_form(form: str, expected_lemma: str) -> bool:

        if not form or len(form) < 2:
            return False

        min_len = min(len(form), len(expected_lemma))
        common = sum(
            1 for a, b in zip(form.lower(), expected_lemma.lower())
            if a == b
        )

        return common >= min_len * 0.6