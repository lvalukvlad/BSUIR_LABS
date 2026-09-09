"""
Генерация словоформ по лемме и морфологическим параметрам
"""

from typing import Optional, Tuple, Dict, List
from core.dictionary.models import LemmaEntry, MorphRule
from core.morphology.analyzer import RussianMorphAnalyzer


class WordFormGenerator:
    """Генератор словоформ с fallback-эвристиками"""

    # Маппинг: русские названия → коды pymorphy2
    GRAMMEME_MAP = {
        'падеж': {
            'именительный': 'nomn', 'родительный': 'gent', 'дательный': 'datv',
            'винительный': 'accs', 'творительный': 'ablt', 'предложный': 'loct',
            'звательный': 'voct',
            # Обратный маппинг
            'nomn': 'nomn', 'gent': 'gent', 'datv': 'datv',
            'accs': 'accs', 'ablt': 'ablt', 'loct': 'loct'
        },
        'число': {'ед': 'sing', 'мн': 'plur', 'sing': 'sing', 'plur': 'plur'},
        'род': {'муж': 'masc', 'жен': 'femn', 'ср': 'neut', 'masc': 'masc', 'femn': 'femn', 'neut': 'neut'},
        'время': {'прошедшее': 'past', 'настоящее': 'pres', 'будущее': 'fut'},
        'лицо': {'1': '1per', '2': '2per', '3': '3per'}
    }

    # Эвристики окончаний для fallback
    FALLBACK_ENDINGS = {
        'существительное': {
            'муж': {
                'sing': {'nomn': '', 'gent': 'а', 'datv': 'у', 'accs': '', 'ablt': 'ом', 'loct': 'е'},
                'plur': {'nomn': 'ы', 'gent': 'ов', 'datv': 'ам', 'accs': 'ы', 'ablt': 'ами', 'loct': 'ах'}
            },
            'жен': {
                'sing': {'nomn': 'а', 'gent': 'ы', 'datv': 'е', 'accs': 'у', 'ablt': 'ой', 'loct': 'е'},
                'plur': {'nomn': 'ы', 'gent': 'ей', 'datv': 'ам', 'accs': 'ы', 'ablt': 'ами', 'loct': 'ах'}
            }
        }
    }

    @staticmethod
    def normalize_grammemes(grammemes: Dict[str, str]) -> Dict[str, str]:
        """Приведение граммем к единому формату (коды pymorphy2)"""
        result = {}
        for key, value in grammemes.items():
            if key in WordFormGenerator.GRAMMEME_MAP:
                normalized = WordFormGenerator.GRAMMEME_MAP[key].get(value, value)
                result[key] = normalized
            else:
                result[key] = value
        return result

    @staticmethod
    def generate(entry: LemmaEntry, grammemes: Dict[str, str]) -> Tuple[Optional[str], Optional[MorphRule]]:
        """
        Генерация словоформы

        Args:
            entry: запись словаря
            grammemes: запрошенные морфологические параметры

        Returns:
            tuple: (сгенерированная форма, использованное правило или None)
        """
        # Нормализуем запрошенные граммемы
        target = WordFormGenerator.normalize_grammemes(grammemes)

        # 1. Поиск точного совпадения правила
        for rule in entry.rules:
            rule_grammemes = WordFormGenerator.normalize_grammemes(rule.grammemes)

            # Проверяем, покрывает ли правило все запрошенные граммемы
            if all(rule_grammemes.get(k) == v for k, v in target.items() if k in rule_grammemes or k in target):
                form = entry.stem + rule.ending
                return form, rule

        # 2. Fallback: эвристическая генерация
        form = WordFormGenerator._fallback_generate(entry, target)
        if form:
            return form, None

        # 3. Возвращаем лемму как последний resort
        return entry.lemma, None

    @staticmethod
    def _fallback_generate(entry: LemmaEntry, target: Dict[str, str]) -> Optional[str]:
        """Эвристическая генерация"""
        pos = entry.pos.lower()
        if pos not in ['существительное', 'noun']:
            return None

        # Определяем род
        gender = 'masc'  # default
        for rule in entry.rules:
            if rule.grammemes.get('род') in ['femn', 'жен']:
                gender = 'femn'
                break
            elif rule.grammemes.get('род') in ['neut', 'ср']:
                gender = 'neut'
                break

        number = target.get('число', 'sing')
        case = target.get('падеж', 'nomn')

        # Таблица окончаний
        endings = {
            'femn': {
                'sing': {'ablt': 'ой', 'datv': 'е', 'gent': 'ы', 'loct': 'е', 'nomn': 'а'},
            },
            'masc': {
                'sing': {'ablt': 'ом', 'datv': 'у', 'gent': 'а', 'loct': 'е', 'nomn': ''},
            }
        }

        ending = endings.get(gender, {}).get(number, {}).get(case)
        if ending is not None:
            # Умное соединение: если основа заканчивается на гласную и окончание тоже — убираем последнюю букву
            stem = entry.stem
            if stem and stem[-1] in 'аоуеыияюё' and ending and ending[0] in 'аоуеыияюё':
                stem = stem[:-1]
            return stem + ending

        return None

    @staticmethod
    def validate_form(form: str, expected_lemma: str) -> bool:
        """
        Простая валидация сгенерированной формы

        Args:
            form: сгенерированная форма
            expected_lemma: ожидаемая лемма

        Returns:
            bool: форма выглядит правдоподобно
        """
        # Минимальная длина
        if len(form) < 2:
            return False

        # Форма должна содержать основу леммы или быть похожей
        if expected_lemma.lower() in form.lower() or form.lower() in expected_lemma.lower():
            return True

        # Разрешаем небольшие различия (окончания)
        min_len = min(len(form), len(expected_lemma))
        common = sum(1 for a, b in zip(form.lower(), expected_lemma.lower()) if a == b)
        return common >= min_len * 0.6  # 60% совпадения