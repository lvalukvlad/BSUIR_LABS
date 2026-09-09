# medicine_provider.py - УЛУЧШЕННАЯ ВЕРСИЯ
from .base_agent import BaseAgent
import json
import logging
import pandas as pd
from typing import Dict, Any, List, Union
import os
try:
    from fuzzywuzzy import fuzz
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False
    fuzz = None
logger = logging.getLogger(__name__)


class MedicineProvider(BaseAgent):
    """Агент подбора лекарств через LLM с поиском по датасету"""

    def __init__(self, llm_client, medicine_data_path: str = None, use_similarity_search: bool = True):
        super().__init__("MedicineProvider", llm_client)
        self.medicine_db = self.load_medicine_database(medicine_data_path)
        self.use_similarity_search = use_similarity_search
        self.medicine_names = self._extract_medicine_names()

    def _extract_medicine_names(self) -> List[str]:
        """Извлекает все названия лекарств для поиска"""
        names = []
        for med in self.medicine_db:
            names.append(med.get('name_ru', ''))
            names.append(med.get('name_en', ''))
            # Добавляем аналоги
            substitutes = med.get('substitutes_ru', [])
            if substitutes:
                names.extend(substitutes)
        return [name for name in names if name]

    def load_medicine_database(self, data_path: str) -> List[Dict]:
        """Загружает базу лекарств из JSON или CSV"""
        medicines = []

        # Путь по умолчанию
        if not data_path:
            data_path = os.path.join('data', 'medicines_ru_full.json')

        try:
            if os.path.exists(data_path):
                if data_path.endswith('.json'):
                    with open(data_path, 'r', encoding='utf-8') as f:
                        medicines = json.load(f)
                    logger.info(f"Loaded {len(medicines)} medicines from JSON")

                elif data_path.endswith('.csv'):
                    df = pd.read_csv(data_path, encoding='utf-8')
                    medicines = self._convert_csv_to_dict(df)
                    logger.info(f"Loaded {len(medicines)} medicines from CSV")

            else:
                logger.warning(f"Medicine database not found at {data_path}")
                medicines = self._create_fallback_database()

        except Exception as e:
            logger.error(f"Failed to load medicine database: {e}")
            medicines = self._create_fallback_database()

        return medicines

    def _convert_csv_to_dict(self, df: pd.DataFrame) -> List[Dict]:
        """Конвертирует CSV в словарь"""
        medicines = []

        for _, row in df.iterrows():
            medicine = {
                'id': int(row.get('id', 0)),
                'name_en': str(row.get('name', '')).strip(),
                'name_ru': self._translate_name(str(row.get('name', ''))),
                'uses_en': self._extract_uses(row),
                'uses_ru': [],  # Будет заполнено переводчиком
                'side_effects_en': self._extract_side_effects(row),
                'side_effects_ru': [],
                'therapeutic_class_en': str(row.get('Therapeutic Class', '')).strip(),
                'therapeutic_class_ru': '',
                'action_class_en': str(row.get('Action Class', '')).strip(),
                'action_class_ru': '',
                'chemical_class': str(row.get('Chemical Class', '')).strip(),
                'habit_forming': str(row.get('Habit Forming', 'No')).strip() == 'Yes',
                'substitutes_en': self._extract_substitutes(row),
                'substitutes_ru': []
            }
            medicines.append(medicine)

        return medicines

    def _translate_name(self, name: str) -> str:
        """Простой перевод названия"""
        translations = {
            'tablet': 'таблетки',
            'syrup': 'сироп',
            'capsule': 'капсулы',
            'cream': 'крем',
            'ointment': 'мазь',
            'suspension': 'суспензия',
            'injection': 'инъекция',
            'drops': 'капли',
            'powder': 'порошок'
        }

        name_lower = name.lower()
        for eng, ru in translations.items():
            if eng in name_lower:
                # Заменяем только суффикс
                name = name.replace(eng, ru)

        return name

    def _extract_uses(self, row: pd.Series) -> List[str]:
        """Извлекает показания к применению"""
        uses = []
        for i in range(5):  # use0-use4
            col = f'use{i}'
            if col in row and pd.notna(row[col]) and str(row[col]).strip():
                uses.append(str(row[col]).strip())
        return uses

    def _extract_side_effects(self, row: pd.Series) -> List[str]:
        """Извлекает побочные эффекты"""
        effects = []
        for i in range(42):  # sideEffect0-41
            col = f'sideEffect{i}'
            if col in row and pd.notna(row[col]) and str(row[col]).strip():
                effects.append(str(row[col]).strip())
        return list(set(effects))[:10]  # Убираем дубли, берем первые 10

    def _extract_substitutes(self, row: pd.Series) -> List[str]:
        """Извлекает аналоги"""
        substitutes = []
        for i in range(5):  # substitute0-4
            col = f'substitute{i}'
            if col in row and pd.notna(row[col]) and str(row[col]).strip():
                substitutes.append(str(row[col]).strip())
        return substitutes

    async def process(self, state: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
        # Извлекаем диагноз
        diagnosis_data = self._extract_diagnosis_data(state)
        diagnosis_text = self._get_diagnosis_text(diagnosis_data)

        logger.info(f"💊 MedicineProvider processing diagnosis: {diagnosis_text}")

        if not diagnosis_text:
            logger.warning("No diagnosis provided")
            return self._empty_result("Нет диагноза для подбора лекарств")

        # Извлекаем симптомы для контекста
        symptoms = self._extract_symptoms(state)

        logger.info(f"   Symptoms: {symptoms[:3]}...")
        logger.info(f"   Medicine DB size: {len(self.medicine_db)}")

        # Ищем релевантные лекарства в датасете
        relevant_medicines = self._find_relevant_medicines(diagnosis_text, symptoms)

        logger.info(f"   Relevant medicines found: {len(relevant_medicines)}")

        # Получаем рекомендации
        if relevant_medicines:
            # Попробуем получить рекомендации через LLM
            recommendations = await self._get_llm_recommendations(
                diagnosis_text,
                symptoms,
                relevant_medicines,
                state
            )
        else:
            # Fallback: простые рекомендации
            logger.warning("No relevant medicines found, using fallback")
            recommendations = self._create_simple_recommendations(diagnosis_text, symptoms)

        # Формируем текстовый ответ
        recommendations_text = self._format_recommendations_text(recommendations, diagnosis_text)

        result = {
            "suggested_medicines": recommendations,
            "database_medicines_found": len(relevant_medicines),
            "recommendation_success": len(recommendations) > 0,
            "diagnosis": diagnosis_text,
            "medicines_count": len(recommendations),
            "used_database": len(relevant_medicines) > 0,
            "recommendations_text": recommendations_text  # Добавляем готовый текст
        }

        logger.info(f"✅ MedicineProvider returning {len(recommendations)} recommendations")

        return result

    def _find_relevant_medicines(self, diagnosis: str, symptoms: List[str]) -> List[Dict]:
        """Ищет релевантные лекарства в датасете - УПРОЩЕННАЯ ВЕРСИЯ"""

        if not self.medicine_db:
            logger.warning("Medicine database is empty")
            return []

        relevant = []

        # Создаем поисковые запросы
        search_terms = []

        # Добавляем ключевые слова из диагноза
        diagnosis_lower = diagnosis.lower()
        diagnosis_keywords = diagnosis_lower.split()
        search_terms.extend(diagnosis_keywords)

        # Добавляем ключевые слова из симптомов
        for symptom in symptoms[:3]:  # Берем первые 3 симптома
            symptom_lower = symptom.lower()
            symptom_keywords = symptom_lower.split()
            search_terms.extend(symptom_keywords)

        # Удаляем стоп-слова
        stop_words = ['и', 'в', 'на', 'с', 'у', 'по', 'для', 'от', 'о', 'об']
        search_terms = [term for term in search_terms if term not in stop_words and len(term) > 2]

        logger.info(f"Searching medicines with terms: {search_terms}")

        # Простой поиск по базе
        for medicine in self.medicine_db:
            score = 0

            # Проверяем название на русском
            name_ru = medicine.get('name_ru', '').lower()
            if any(term in name_ru for term in search_terms):
                score += 50

            # Проверяем показания
            uses_ru = medicine.get('uses_ru', [])
            for use in uses_ru:
                use_lower = use.lower()
                for term in search_terms:
                    if term in use_lower:
                        score += 30

            # Проверяем класс
            therapeutic_class = medicine.get('therapeutic_class_ru', '').lower()
            for term in search_terms:
                if term in therapeutic_class:
                    score += 20

            # Если есть хотя бы некоторое совпадение
            if score > 30:
                medicine['relevance_score'] = score
                relevant.append(medicine)

        # Сортируем по релевантности
        relevant.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        logger.info(f"Found {len(relevant)} relevant medicines")

        return relevant[:10]  # Возвращаем топ-10

    def _calculate_relevance_score(self, medicine: Dict, search_terms: List[str]) -> float:
        """Вычисляет релевантность лекарства"""
        score = 0

        # Проверяем названия
        name_ru = medicine.get('name_ru', '').lower()
        name_en = medicine.get('name_en', '').lower()

        # Проверяем показания
        uses_ru = [use.lower() for use in medicine.get('uses_ru', [])]
        uses_en = [use.lower() for use in medicine.get('uses_en', [])]

        all_text = ' '.join([name_ru, name_en] + uses_ru + uses_en)

        for term in search_terms:
            # Fuzzy match по всему тексту
            match_score = fuzz.partial_ratio(term, all_text)
            score += match_score

            # Бонус за точное совпадение в показаниях
            if any(term in use for use in uses_ru + uses_en):
                score += 50

        return score

    def _get_match_reason(self, medicine: Dict, search_terms: List[str]) -> str:
        """Определяет почему лекарство релевантно"""
        reasons = []

        for term in search_terms:
            # Проверяем показания
            uses_ru = [use.lower() for use in medicine.get('uses_ru', [])]
            uses_en = [use.lower() for use in medicine.get('uses_en', [])]

            if any(term in use for use in uses_ru):
                reasons.append(f"Показание: {term}")
            elif any(term in use for use in uses_en):
                reasons.append(f"Indication: {term}")

        return ', '.join(reasons[:2]) if reasons else "Общее совпадение"

    async def _get_llm_recommendations(self, diagnosis: str, symptoms: List[str],
                                       relevant_medicines: List[Dict], state: Any) -> List[Dict]:
        """Получает рекомендации через LLM с учетом найденных лекарств"""

        # Форматируем найденные лекарства для промпта
        medicines_text = ""
        if relevant_medicines:
            medicines_text = "ПРЕПАРАТЫ ИЗ БАЗЫ ДАННЫХ:\n"
            for i, med in enumerate(relevant_medicines[:5], 1):
                name = med.get('name_ru') or med.get('name_en', 'Неизвестно')
                uses = med.get('uses_ru', med.get('uses_en', []))
                class_info = med.get('therapeutic_class_ru') or med.get('therapeutic_class_en', '')

                medicines_text += f"{i}. {name}\n"
                if uses:
                    medicines_text += f"   Показания: {', '.join(uses[:2])}\n"
                if class_info:
                    medicines_text += f"   Класс: {class_info}\n"
                medicines_text += "\n"

        symptoms_text = ', '.join(symptoms[:5])

        prompt = f"""Как клинический фармаколог, подбери лекарства для диагноза:

ДИАГНОЗ: {diagnosis}
СИМПТОМЫ: {symptoms_text}

{medicines_text}

ИНСТРУКЦИИ:
1. Используй информацию из базы данных выше если она релевантна
2. Учитывай безопасность и противопоказания
3. Предложи 2-3 наиболее подходящих препарата
4. Для каждого укажи:
   - Почему он подходит
   - Дозировку для начала лечения
   - Меры предосторожности
   - Альтернативы если есть

ФОРМАТ JSON:
{{
    "recommendations": [
        {{
            "name": "Название препарата (на русском)",
            "reason": "Почему подходит для диагноза",
            "dosage": "Рекомендуемая дозировка",
            "precautions": "Меры предосторожности",
            "alternatives": ["альтернатива1", "альтернатива2"],
            "is_from_database": true/false
        }}
    ],
    "general_advice": "Общие рекомендации"
}}"""

        response = await self.generate_with_llm(
            prompt=prompt,
            system_prompt="Ты - опытный клинический фармаколог. Используй научно-обоснованные рекомендации.",
            max_tokens=800
        )

        if not response:
            return self._get_database_fallback(relevant_medicines)

        try:
            recommendations = self._parse_recommendations(response)

            # Обогащаем рекомендации данными из базы
            enriched = self._enrich_with_database_info(recommendations, relevant_medicines)

            return enriched[:3]  # Максимум 3 рекомендации

        except Exception as e:
            logger.error(f"Failed to parse recommendations: {e}")
            return self._get_database_fallback(relevant_medicines)

    # Добавить в класс MedicineProvider недостающие методы:

    def _get_diagnosis_text(self, diagnosis_data: Any) -> str:
        """Извлекает текст диагноза"""
        # Если это DiagnosisInfo объект (имеет атрибут name)
        if hasattr(diagnosis_data, 'name'):
            return getattr(diagnosis_data, 'name', '')
        # Если это словарь
        elif isinstance(diagnosis_data, dict):
            return diagnosis_data.get('diagnosis', diagnosis_data.get('name', ''))
        return ""

    def _extract_diagnosis_data(self, state: Any) -> Any:
        """Извлекает данные диагноза"""
        # Если это объект (например, ConversationContext)
        if hasattr(state, 'primary_diagnosis'):
            return getattr(state, 'primary_diagnosis')
        elif hasattr(state, 'preliminary_diagnosis'):
            return getattr(state, 'preliminary_diagnosis')
        # Если это словарь
        elif isinstance(state, dict):
            # Проверяем primary_diagnosis в словаре
            primary = state.get('primary_diagnosis')
            if primary:
                return primary
            # Проверяем preliminary_diagnosis
            prelim = state.get('preliminary_diagnosis')
            if prelim:
                return prelim
        return {}

    def _extract_symptoms(self, state: Any) -> List[str]:
        """Извлекает симптомы"""
        if hasattr(state, 'get_symptoms_for_processing'):
            return state.get_symptoms_for_processing()
        elif hasattr(state, 'symptom_texts'):
            return getattr(state, 'symptom_texts', [])
        elif isinstance(state, dict):
            return state.get('symptom_texts', [])
        return []

    def _parse_recommendations(self, response: str) -> List[Dict]:
        """Парсит рекомендации из ответа LLM"""
        try:
            import json
            import re

            # Ищем JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data.get('recommendations', [])
        except:
            pass
        return []

    def _empty_result(self, reason: str) -> Dict[str, Any]:
        """Создает пустой результат"""
        return {
            "suggested_medicines": [],
            "database_medicines_found": 0,
            "recommendation_success": False,
            "diagnosis": "",
            "error": reason
        }

    def _create_fallback_database(self) -> List[Dict]:
        """Создает fallback базу данных"""
        return [
            {
                "id": 1,
                "name_ru": "Парацетамол",
                "name_en": "Paracetamol",
                "uses_ru": ["Боль", "Лихорадка"],
                "therapeutic_class_ru": "Жаропонижающие"
            }
        ]

    def _enrich_with_database_info(self, recommendations: List[Dict],
                                   database_medicines: List[Dict]) -> List[Dict]:
        """Обогащает рекомендации данными из базы - УПРОЩЕННАЯ ВЕРСИЯ"""

        if not database_medicines:
            return recommendations

        enriched = []

        for rec in recommendations:
            rec_name = rec.get('name', '').lower()

            # Ищем лучший матч в базе
            best_match = None
            best_score = 0

            for med in database_medicines:
                name_ru = med.get('name_ru', '').lower()

                # Простое сравнение строк
                if rec_name in name_ru or name_ru in rec_name:
                    score = 100
                else:
                    # Более сложное сравнение (можно упростить)
                    common_words = set(rec_name.split()) & set(name_ru.split())
                    score = len(common_words) * 20

                if score > best_score and score > 40:
                    best_score = score
                    best_match = med

            if best_match:
                # Обогащаем рекомендацию
                enriched_rec = rec.copy()
                enriched_rec.update({
                    'database_info': {
                        'id': best_match.get('id'),
                        'name_ru': best_match.get('name_ru'),
                        'name_en': best_match.get('name_en'),
                        'uses': best_match.get('uses_ru', []),
                        'side_effects': best_match.get('side_effects_ru', []),
                        'therapeutic_class': best_match.get('therapeutic_class_ru', '')
                    },
                    'is_from_database': True
                })
            else:
                enriched_rec = rec
                enriched_rec['is_from_database'] = False

            enriched.append(enriched_rec)

        return enriched

    def _get_database_fallback(self, relevant_medicines: List[Dict]) -> List[Dict]:
        """Fallback: используем лекарства из базы данных напрямую"""
        if not relevant_medicines:
            return []

        recommendations = []
        for med in relevant_medicines[:3]:  # Берем топ-3
            name = med.get('name_ru') or med.get('name_en', 'Неизвестно')
            uses = med.get('uses_ru', med.get('uses_en', []))

            recommendation = {
                'name': name,
                'reason': f"Используется для: {', '.join(uses[:2])}" if uses else "Стандартное лечение",
                'dosage': 'По назначению врача',
                'precautions': 'Проконсультируйтесь с врачом',
                'alternatives': med.get('substitutes_ru', med.get('substitutes_en', [])),
                'is_from_database': True,
                'database_info': {
                    'id': med.get('id'),
                    'name_ru': med.get('name_ru'),
                    'name_en': med.get('name_en'),
                    'uses': uses,
                    'side_effects': med.get('side_effects_ru', med.get('side_effects_en', [])),
                    'therapeutic_class': med.get('therapeutic_class_ru', med.get('therapeutic_class_en', ''))
                }
            }
            recommendations.append(recommendation)

        return recommendations


    def _create_simple_recommendations(self, diagnosis: str, symptoms: List[str]) -> List[Dict]:
        """Создает простые рекомендации на основе диагноза"""

        # Базовые рекомендации для частых диагнозов
        common_recommendations = {
            "фарингит": [
                {
                    "name": "Парацетамол",
                    "reason": "Для снижения температуры и обезболивания",
                    "dosage": "500 мг 3-4 раза в день",
                    "precautions": "Не превышать 4 г в сутки",
                    "alternatives": ["Ибупрофен", "Аспирин"]
                },
                {
                    "name": "Граммидин",
                    "reason": "Местное лечение боли в горле",
                    "dosage": "1 таблетка 3-4 раза в день",
                    "precautions": "Рассасывать после еды",
                    "alternatives": ["Стрепсилс", "Фарингосепт"]
                }
            ],
            "орви": [
                {
                    "name": "Парацетамол",
                    "reason": "Жаропонижающее и обезболивающее",
                    "dosage": "500 мг каждые 6-8 часов",
                    "precautions": "Не сочетать с алкоголем",
                    "alternatives": ["Ибупрофен"]
                },
                {
                    "name": "Аскорбиновая кислота",
                    "reason": "Поддержка иммунитета",
                    "dosage": "1000 мг в сутки",
                    "precautions": "Принимать после еды",
                    "alternatives": ["Цинк", "Витамин D"]
                }
            ]
        }

        # Ищем подходящие рекомендации
        diagnosis_lower = diagnosis.lower()

        for key, recommendations in common_recommendations.items():
            if key in diagnosis_lower:
                return recommendations

        # Возвращаем общие рекомендации
        return [
            {
                "name": "Парацетамол",
                "reason": "Обезболивающее и жаропонижающее",
                "dosage": "По назначению врача",
                "precautions": "Проконсультируйтесь с врачом",
                "alternatives": []
            }
        ]


    def _format_recommendations_text(self, recommendations: List[Dict], diagnosis: str) -> str:
        """Форматирует рекомендации в текст"""

        text = f"💊 **Рекомендации по лечению ({diagnosis}):**\n\n"

        if not recommendations:
            text += "Рекомендуется обратиться к врачу для назначения лечения.\n"
            return text

        for i, med in enumerate(recommendations[:3], 1):
            text += f"{i}. **{med.get('name', 'Препарат')}**\n"

            if med.get('reason'):
                text += f"   📋 *Применение:* {med.get('reason')}\n"

            if med.get('dosage'):
                text += f"   💊 *Дозировка:* {med.get('dosage')}\n"

            if med.get('precautions'):
                text += f"   ⚠️ *Меры предосторожности:* {med.get('precautions')}\n"

            if med.get('alternatives'):
                alts = med.get('alternatives', [])
                if alts:
                    text += f"   🔄 *Альтернативы:* {', '.join(alts[:3])}\n"

            text += "\n"

        text += "**Общие рекомендации:**\n"
        text += "• Проконсультируйтесь с врачом перед применением\n"
        text += "• Соблюдайте дозировку\n"
        text += "• При ухудшении состояния обратитесь за помощью\n\n"

        text += "⚠️ **Это предварительные рекомендации. Для точного лечения обратитесь к врачу.**"

        return text
