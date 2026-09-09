import pandas as pd
import json
from typing import Dict, List
import re


class HybridMedicineProcessor:

    MEDICAL_DICTIONARY = {
        'tablet': 'таблетки',
        'capsule': 'капсулы',
        'syrup': 'сироп',
        'injection': 'инъекция',
        'cream': 'крем',
        'ointment': 'мазь',
        'antibiotic': 'антибиотик',
        'analgesic': 'обезболивающее',
        'antipyretic': 'жаропонижающее',
        'antihistamine': 'антигистаминное',
        'antiviral': 'противовирусное',
        'antifungal': 'противогрибковое',
        'infection': 'инфекция',
        'pain': 'боль',
        'fever': 'лихорадка',
        'inflammation': 'воспаление',
        'allergy': 'аллергия',
        'cough': 'кашель',
    }

    KNOWN_DRUGS = {
        'augmentin': 'Аугментин',
        'amoxiclav': 'Амоксиклав',
        'azithromycin': 'Азитромицин',
        'ceftriaxone': 'Цефтриаксон',
        'paracetamol': 'Парацетамол',
        'ibuprofen': 'Ибупрофен',
        'omeprazole': 'Омепразол',
        'loratadine': 'Лоратадин',
    }

    async def process_large_dataset(self, csv_path: str,
                                    output_path: str,
                                    sample_size: int = 5000,
                                    use_llm_for_complex: bool = True):

        print(f"📊 Загрузка датасета из {csv_path}...")
        df = pd.read_csv(csv_path)
        print(f"✅ Загружено {len(df):,} записей")

        if sample_size < len(df):
            sample_df = self._create_strategic_sample(df, sample_size)
        else:
            sample_df = df

        print(f"🔍 Обрабатываю выборку из {len(sample_df):,} лекарств")

        grouped = self._group_by_class(sample_df)

        all_translations = []

        for class_name, group_df in grouped.items():
            print(f"📦 Обрабатываю класс: {class_name} ({len(group_df)} лекарств)")

            group_translations = self._translate_group_rule_based(group_df)

            if use_llm_for_complex:
                complex_drugs = self._identify_complex_drugs(group_df)
                if complex_drugs:
                    print(f"   🤖 Перевод сложных через LLM: {len(complex_drugs)}")
                    llm_translations = await self._translate_complex_with_llm(complex_drugs)

            all_translations.extend(group_translations)

            if len(all_translations) % 1000 == 0:
                self._save_progress(all_translations, output_path)

        self._save_final(all_translations, output_path)

        self._create_lookup_table(all_translations)

        return all_translations

    def _create_strategic_sample(self, df: pd.DataFrame, sample_size: int) -> pd.DataFrame:

        samples = []

        first_n = min(2000, sample_size // 2)
        samples.append(df.head(first_n))

        if 'Therapeutic Class' in df.columns:
            classes = df['Therapeutic Class'].dropna().unique()
            for cls in classes[:1000]:
                class_sample = df[df['Therapeutic Class'] == cls].head(1)
                samples.append(class_sample)

        if sample_size - len(pd.concat(samples)) > 1000:
            random_sample = df.sample(n=min(1000, len(df) // 10))
            samples.append(random_sample)

        result = pd.concat(samples).drop_duplicates(subset=['name'])
        return result.head(sample_size)

    def _translate_group_rule_based(self, df_group: pd.DataFrame) -> List[Dict]:
        translations = []

        for _, row in df_group.iterrows():
            name = str(row.get('name', '')).lower()

            translated_name = self._lookup_known_drug(name)

            if not translated_name:
                translated_name = self._rule_based_translation(name)

            uses_ru = self._translate_uses_rule_based(row)

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
        name_lower = name.lower()

        for eng, ru in self.KNOWN_DRUGS.items():
            if eng in name_lower:
                return name_lower.replace(eng, ru)

        for eng, ru in self.KNOWN_DRUGS.items():
            if eng.split()[0] in name_lower.split():
                return ru + ' ' + ' '.join(name_lower.split()[1:])

        return ""

    def _rule_based_translation(self, name: str) -> str:
        parts = name.split()
        translated_parts = []

        for part in parts:
            part_lower = part.lower()

            if part_lower in self.MEDICAL_DICTIONARY:
                translated_parts.append(self.MEDICAL_DICTIONARY[part_lower])
            elif part_lower.endswith(('cin', 'mycin', 'cycline')):
                translated_parts.append(f"{part} (антибиотик)")
            elif part_lower.endswith('profen'):
                translated_parts.append(f"{part} (противовоспалительное)")
            else:
                translated_parts.append(part)

        return ' '.join(translated_parts)

    def _translate_uses_rule_based(self, row: pd.Series) -> List[str]:
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
        term_lower = term.lower()

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