import pymorphy3 as pymorphy2
from typing import Optional, Tuple, List


class StemExtractor:
    ENDINGS = {
        'существительное': {
            'муж': {'а', 'я', 'у', 'ю', 'е', 'о', 'ом', 'ем', 'у', 'ю', 'ы', 'и', 'ей', 'ям', 'ами', 'ях', 'ах'},
            'жен': {'ы', 'и', 'е', 'ю', 'у', 'ой', 'ей', 'ей', 'ам', 'ами', 'ах', 'а', 'я'},
            'ср': {'а', 'я', 'у', 'ю', 'е', 'о', 'ом', 'ем', 'а', 'я', 'ам', 'ами', 'ах'}
        },
        'прилагательное': {
            'ый', 'ий', 'ой', 'ая', 'яя', 'ое', 'ее', 'ого', 'его', 'ому', 'ему',
            'ым', 'им', 'ою', 'ею', 'ом', 'ем', 'ые', 'ие'
        },
        'глагол': {
            'ть', 'ти', 'чь', 'ю', 'у', 'ешь', 'ёшь', 'ет', 'ёт', 'ём', 'ём',
            'ете', 'ёте', 'ут', 'ют', 'ат', 'ят', 'л', 'ла', 'ло', 'ли', ' бы'
        }
    }

    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()

    def extract(self, word: str, lemma: Optional[str] = None, pos: Optional[str] = None) -> str:
        if lemma is None or pos is None:
            parse = self.morph.parse(word)[0]
            lemma = lemma or parse.normal_form
            pos_raw = parse.tag.POS or ''
            pos_map = {'NOUN': 'существительное', 'ADJF': 'прилагательное', 'VERB': 'глагол'}
            pos = pos_map.get(pos_raw, pos_raw)

        if word.lower() == lemma.lower():
            return lemma

        stem = self._extract_by_ending(word, lemma, pos)
        if stem and len(stem) >= 2:
            return stem
        return lemma

    def _extract_by_ending(self, word: str, lemma: str, pos: str) -> Optional[str]:
        word_lower = word.lower()
        lemma_lower = lemma.lower()

        possible_endings = self.ENDINGS.get(pos, set())

        sorted_endings = sorted(possible_endings, key=len, reverse=True)

        for ending in sorted_endings:
            if word_lower.endswith(ending):
                potential_stem = word_lower[:-len(ending)] if ending else word_lower

                if lemma_lower.startswith(potential_stem) or potential_stem.startswith(
                        lemma_lower[:len(potential_stem)]):
                    return potential_stem

        return None

    def extract_with_ending(self, word: str, lemma: str) -> Tuple[str, str]:
        min_len = min(len(word), len(lemma))
        common_len = 0
        for i in range(min_len):
            if word[i].lower() == lemma[i].lower():
                common_len += 1
            else:
                break

        if common_len >= 2:
            stem = word[:common_len]
            ending = word[common_len:]
            return stem, ending

        return lemma, ""

    def get_possible_forms(self, lemma: str, pos: str, grammemes: dict) -> List[str]:
        forms = []
        stem = self.extract(lemma, lemma, pos)

        if pos == 'существительное':
            gender = grammemes.get('род', 'муж')
            number = grammemes.get('число', 'ед')
            case = grammemes.get('падеж', '')

            endings_map = {
                ('муж', 'ед', 'именительный'): '',
                ('муж', 'ед', 'родительный'): 'а',
                ('муж', 'ед', 'дательный'): 'у',
                ('муж', 'ед', 'винительный'): '',
                ('муж', 'ед', 'творительный'): 'ом',
                ('муж', 'ед', 'предложный'): 'е',
                ('жен', 'ед', 'именительный'): 'а',
                ('жен', 'ед', 'родительный'): 'ы',
                ('жен', 'ед', 'дательный'): 'е',
                ('жен', 'ед', 'творительный'): 'ой',
                ('жен', 'ед', 'предложный'): 'е',
            }

            key = (gender, number, case)
            if key in endings_map:
                forms.append(stem + endings_map[key])

        return forms if forms else [lemma]