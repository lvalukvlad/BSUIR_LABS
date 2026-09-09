# hybrid_medicine_processor.py
import pandas as pd
import json
from typing import Dict, List
import re


class HybridMedicineProcessor:
    """
    Обрабатывает огромный датасет лекарств:
    1. Быстрый rule-based перевод частых терминов
    2. LLM только для сложных случаев
    3. Группировка по классам
    """

    # Предзагруженные медицинские словари
    MEDICAL_DICTIONARY = {
        # Действия
        'tablet': 'таблетки',
        'capsule': 'капсулы',
        'syrup': 'сироп',
        'injection': 'инъекция',
        'cream': 'крем',
        'ointment': 'мазь',

        # Классы
        'antibiotic': 'антибиотик',
        'analgesic': 'обезболивающее',
        'antipyretic': 'жаропонижающее',
        'antihistamine': 'антигистаминное',
        'antiviral': 'противовирусное',
        'antifungal': 'противогрибковое',

        # Показания
        'infection': 'инфекция',
        'pain': 'боль',
        'fever': 'лихорадка',
        'inflammation': 'воспаление',
        'allergy': 'аллергия',
        'cough': 'кашель',
    }

    # Известные торговые названия (ручное добавление)
    KNOWN_DRUGS = {
        'augmentin': 'Аугментин',
        'amoxiclav': 'Амоксиклав',
        'azithromycin': 'Азитромицин',
        'ceftriaxone': 'Цефтриаксон',
        'paracetamol': 'Парацетамол',
        'ibuprofen': 'Ибупрофен',
        'omeprazole': 'Омепразол',
        'loratadine': 'Лоратадин',
        # Добавьте 100-200 самых частых
    }

    async def process_large_dataset(self, csv_path: str,
                                    output_path: str,
                                    sample_size: int = 5000,
                                    use_llm_for_complex: bool = True):
        """
        Обрабатывает огромный датасет:
        - sample_size: сколько лекарств обрабатывать (рекомендую 5000-10000)
        """

        print(f"📊 Загрузка датасета из {csv_path}...")
        df = pd.read_csv(csv_path)
        print(f"✅ Загружено {len(df):,} записей")

        # 1. Выбираем репрезентативную выборку
        if sample_size < len(df):
            # Стратегическая выборка:
            # - Первые N (часто самые популярные)
            # - По одному из каждого класса
            # - Уникальные названия

            sample_df = self._create_strategic_sample(df, sample_size)
        else:
            sample_df = df

        print(f"🔍 Обрабатываю выборку из {len(sample_df):,} лекарств")

        # 2. Группируем по классам для batch-обработки
        grouped = self._group_by_class(sample_df)

        # 3. Обрабатываем каждую группу
        all_translations = []

        for class_name, group_df in grouped.items():
            print(f"📦 Обрабатываю класс: {class_name} ({len(group_df)} лекарств)")

            # Быстрый rule-based перевод для группы
            group_translations = self._translate_group_rule_based(group_df)

            # При необходимости добавляем LLM для сложных случаев
            if use_llm_for_complex:
                complex_drugs = self._identify_complex_drugs(group_df)
                if complex_drugs:
                    print(f"   🤖 Перевод сложных через LLM: {len(complex_drugs)}")
                    llm_translations = await self._translate_complex_with_llm(complex_drugs)
                    # Обновляем переводы
                    # ...

            all_translations.extend(group_translations)

            # Сохраняем прогресс
            if len(all_translations) % 1000 == 0:
                self._save_progress(all_translations, output_path)

        # 4. Сохраняем результат
        self._save_final(all_translations, output_path)

        # 5. Создаем lookup таблицу для быстрого поиска
        self._create_lookup_table(all_translations)

        return all_translations

    def _create_strategic_sample(self, df: pd.DataFrame, sample_size: int) -> pd.DataFrame:
        """Создает стратегическую выборку"""

        samples = []

        # 1. Берем первые N (обычно самые частые)
        first_n = min(2000, sample_size // 2)
        samples.append(df.head(first_n))

        # 2. По одному из каждого терапевтического класса
        if 'Therapeutic Class' in df.columns:
            classes = df['Therapeutic Class'].dropna().unique()
            for cls in classes[:1000]:  # Ограничиваем
                class_sample = df[df['Therapeutic Class'] == cls].head(1)
                samples.append(class_sample)

        # 3. Уникальные по названию (первые слова)
        if sample_size - len(pd.concat(samples)) > 1000:
            # Берем случайную выборку для разнообразия
            random_sample = df.sample(n=min(1000, len(df) // 10))
            samples.append(random_sample)

        # Объединяем и удаляем дубли
        result = pd.concat(samples).drop_duplicates(subset=['name'])
        return result.head(sample_size)

    def _translate_group_rule_based(self, df_group: pd.DataFrame) -> List[Dict]:
        """Rule-based перевод группы лекарств"""
        translations = []

        for _, row in df_group.iterrows():
            name = str(row.get('name', '')).lower()

            # 1. Проверяем известные препараты
            translated_name = self._lookup_known_drug(name)

            if not translated_name:
                # 2. Rule-based перевод
                translated_name = self._rule_based_translation(name)

            # 3. Перевод показаний
            uses_ru = self._translate_uses_rule_based(row)

            # 4. Собираем результат
            translation = {
                'id': row.get('id'),
                'name_en': row.get('name'),
                'name_ru': translated_name,
                'uses_ru': uses_ru,
                'therapeutic_class_en': row.get('Therapeutic Class', ''),
                'therapeutic_class_ru': self._translate_class(row.get('Therapeutic Class', '')),
                'is_rule_based': True,
                'translation_confidence': self._calculate_confidence(name, translated_name)
            }

            translations.append(translation)

        return translations

    def _lookup_known_drug(self, name: str) -> str:
        """Поиск в базе известных препаратов"""
        name_lower = name.lower()

        # Прямое совпадение
        for eng, ru in self.KNOWN_DRUGS.items():
            if eng in name_lower:
                # Заменяем часть названия
                return name_lower.replace(eng, ru)

        # Частичное совпадение
        for eng, ru in self.KNOWN_DRUGS.items():
            if eng.split()[0] in name_lower.split():
                return ru + ' ' + ' '.join(name_lower.split()[1:])

        return ""

    def _rule_based_translation(self, name: str) -> str:
        """Rule-based перевод названия"""
        parts = name.split()
        translated_parts = []

        for part in parts:
            part_lower = part.lower()

            # Пробуем перевести каждую часть
            if part_lower in self.MEDICAL_DICTIONARY:
                translated_parts.append(self.MEDICAL_DICTIONARY[part_lower])
            elif part_lower.endswith(('cin', 'mycin', 'cycline')):
                # Антибиотики
                translated_parts.append(f"{part} (антибиотик)")
            elif part_lower.endswith('profen'):
                # НПВП
                translated_parts.append(f"{part} (противовоспалительное)")
            else:
                # Оставляем как есть
                translated_parts.append(part)

        return ' '.join(translated_parts)

    def _translate_uses_rule_based(self, row: pd.Series) -> List[str]:
        """Rule-based перевод показаний"""
        uses_en = []
        for i in range(5):
            col = f'use{i}'
            if col in row and pd.notna(row[col]):
                use_en = str(row[col])
                use_ru = self._translate_medical_term(use_en)
                if use_ru:
                    uses_en.append(use_ru)

        return uses_en or ["Лекарственный препарат"]

    def _translate_medical_term(self, term: str) -> str:
        """Переводит медицинский термин"""
        term_lower = term.lower()

        # Простой словарь
        term_dict = {
            'treatment of': 'Лечение',
            'bacterial infections': 'бактериальных инфекций',
            'pain': 'боли',
            'fever': 'лихорадки',
            'inflammation': 'воспаления',
            'cough': 'кашля',
            'allergy': 'аллергии',
            'asthma': 'астмы',
            'hypertension': 'гипертонии',
            'diabetes': 'диабета',
            'infection': 'инфекции'
        }

        translated = term
        for eng, ru in term_dict.items():
            if eng in term_lower:
                translated = translated.lower().replace(eng, ru)

        return translated.capitalize()