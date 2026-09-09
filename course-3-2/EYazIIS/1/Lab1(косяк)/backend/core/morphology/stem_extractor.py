"""
Извлечение основы слова для русского языка
С учётом окончаний существительных, прилагательных, глаголов
"""

import pymorphy2
from typing import Optional, Tuple, List


class StemExtractor:
    """Умное извлечение основы с учётом морфологии"""

    # Типичные окончания для разных частей речи
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
        """
        Извлечение основы слова с учётом части речи и рода

        Args:
            word: исходная словоформа
            lemma: лемма (если известна)
            pos: часть речи (если известна)

        Returns:
            str: основа слова
        """
        if lemma is None or pos is None:
            # Автоопределение через pymorphy2
            parse = self.morph.parse(word)[0]
            lemma = lemma or parse.normal_form
            pos_raw = parse.tag.POS or ''
            # Маппинг pymorphy2 → русские названия
            pos_map = {'NOUN': 'существительное', 'ADJF': 'прилагательное', 'VERB': 'глагол'}
            pos = pos_map.get(pos_raw, pos_raw)

        # Если слово совпадает с леммой — основа = лемма
        if word.lower() == lemma.lower():
            return lemma

        # Пробуем найти окончание и отделить основу
        stem = self._extract_by_ending(word, lemma, pos)
        if stem and len(stem) >= 2:  # Минимальная длина основы
            return stem

        # Fallback: возвращаем лемму
        return lemma

    def _extract_by_ending(self, word: str, lemma: str, pos: str) -> Optional[str]:
        """Попытка выделить основу через поиск окончания"""
        word_lower = word.lower()
        lemma_lower = lemma.lower()

        # Получаем возможные окончания для этой части речи
        possible_endings = self.ENDINGS.get(pos, set())

        # Сортируем по длине (сначала пробуем более длинные окончания)
        sorted_endings = sorted(possible_endings, key=len, reverse=True)

        for ending in sorted_endings:
            if word_lower.endswith(ending):
                # Проверяем, что оставшаяся часть похожа на основу леммы
                potential_stem = word_lower[:-len(ending)] if ending else word_lower

                # Эвристика: основа должна быть префиксом леммы или наоборот
                if lemma_lower.startswith(potential_stem) or potential_stem.startswith(
                        lemma_lower[:len(potential_stem)]):
                    return potential_stem

        return None

    def extract_with_ending(self, word: str, lemma: str) -> Tuple[str, str]:
        """
        Извлечение основы и окончания

        Returns:
            tuple: (основа, окончание)
        """
        # Простой метод: ищем общую часть
        min_len = min(len(word), len(lemma))

        # Находим длину общего префикса
        common_len = 0
        for i in range(min_len):
            if word[i].lower() == lemma[i].lower():
                common_len += 1
            else:
                break

        if common_len >= 2:  # Минимум 2 символа для основы
            stem = word[:common_len]
            ending = word[common_len:]
            return stem, ending

        # Fallback
        return lemma, ""

    def get_possible_forms(self, lemma: str, pos: str, grammemes: dict) -> List[str]:
        """
        Генерация возможных форм слова по граммемам

        Args:
            lemma: лемма
            pos: часть речи
            grammemes: {падеж: ..., число: ..., род: ...}

        Returns:
            List[str]: список возможных форм
        """
        forms = []
        stem = self.extract(lemma, lemma, pos)

        # Простые эвристики для существительных
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