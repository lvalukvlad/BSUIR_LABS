from .base_agent import BaseAgent
import json
import logging
from typing import Dict, Any, List, Union, Optional
import os

logger = logging.getLogger(__name__)


class MedicineProvider(BaseAgent):
    def __init__(self, llm_client, medicine_data_path: str = None):
        super().__init__("MedicineProvider", llm_client)
        self.medicine_db = self.load_medicine_database(medicine_data_path)
        self.medicine_names = self._extract_medicine_names()

    def _extract_medicine_names(self) -> List[str]:
        names = []
        for med in self.medicine_db:
            name_ru = med.get('name_ru', '')
            if name_ru:
                names.append(name_ru)
            substitutes = med.get('substitutes_ru', [])
            if substitutes:
                names.extend(substitutes)
        return [name for name in names if name]

    def load_medicine_database(self, data_path: str) -> List[Dict]:
        medicines = []

        if not data_path:
            data_path = os.path.join('data', 'medicines_ru_top500.json')

        logger.info(f"📂 Загрузка базы лекарств из: {data_path}")

        try:
            if os.path.exists(data_path):
                logger.info(f"✅ Файл базы данных существует: {data_path}")

                with open(data_path, 'r', encoding='utf-8') as f:
                    medicines = json.load(f)

                logger.info(f"✅ Загружено {len(medicines)} лекарств из JSON")

                if medicines:
                    logger.info(f"📊 Примеры лекарств (первые 3):")
                    for i, med in enumerate(medicines[:3], 1):
                        name = med.get('name_ru', 'Без названия')
                        class_ru = med.get('therapeutic_class_ru', 'Без класса')
                        uses = med.get('uses_ru', [])
                        uses_text = uses[:2] if uses else []
                        logger.info(f"   {i}. {name}")
                        logger.info(f"      Класс: {class_ru}")
                        if uses_text:
                            logger.info(f"      Показания: {', '.join(uses_text)}")
            else:
                logger.warning(f"Файл базы лекарств не найден по пути: {data_path}")

                alt_paths = [
                    os.path.join(os.path.dirname(__file__), '..', 'data', 'medicines_ru_top500.json'),
                    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'medicines_ru_top500.json'),
                    'medicines_ru_top500.json'
                ]

                for alt_path in alt_paths:
                    if os.path.exists(alt_path):
                        logger.info(f"Пробуем альтернативный путь: {alt_path}")
                        with open(alt_path, 'r', encoding='utf-8') as f:
                            medicines = json.load(f)
                        logger.info(f"Загружено {len(medicines)} лекарств из альтернативного пути")
                        break
                else:
                    logger.error(f"Не найден файл базы лекарств ни по одному из путей")
                    medicines = self._create_fallback_database()

        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON: {e}")
            medicines = self._create_fallback_database()
        except Exception as e:
            logger.error(f"Ошибка загрузки базы лекарств: {e}", exc_info=True)
            medicines = self._create_fallback_database()

        return medicines

    def _format_recommendations_text(self, recommendations: List[Dict], diagnosis: str,
                                     contraindications: Dict = None) -> str:
        text = f"**Рекомендации по лечению ({diagnosis}):**\n\n"

        if not recommendations:
            text += "Рекомендуется обратиться к врачу для назначения лечения.\n"
            return text

        if contraindications:
            text += "📋 **Учтены ваши противопоказания:**\n"
            if contraindications.get('allergies') and contraindications['allergies'] != 'нет':
                allergies = contraindications['allergies']
                if isinstance(allergies, list):
                    text += f"• Аллергии: {', '.join(allergies)}\n"
                else:
                    text += f"• Аллергии: {allergies}\n"

            if contraindications.get('chronic_conditions') and contraindications['chronic_conditions'] != 'нет':
                conditions = contraindications['chronic_conditions']
                if isinstance(conditions, list):
                    text += f"• Хронические заболевания: {', '.join(conditions)}\n"
                else:
                    text += f"• Хронические заболевания: {conditions}\n"

            if contraindications.get('pregnancy') is True:
                text += "• Беременность\n"

            if contraindications.get('breastfeeding') is True:
                text += "• Грудное вскармливание\n"

            text += "\n"

        for i, med in enumerate(recommendations[:3], 1):
            text += f"{i}. **{med.get('name', 'Препарат')}**\n"

            if med.get('reason'):
                text += f"   *Применение:* {med.get('reason')}\n"

            if med.get('dosage'):
                text += f"   *Дозировка:* {med.get('dosage')}\n"

            if med.get('precautions'):
                text += f"   *Меры предосторожности:* {med.get('precautions')}\n"

            if med.get('alternatives'):
                alts = med.get('alternatives', [])
                if alts:
                    text += f"   *Альтернативы:* {', '.join(alts[:2])}\n"

            if med.get('is_from_llm'):
                text += f"   *Сгенерировано ИИ*\n"
            elif med.get('is_from_database'):
                text += f"   *Из базы лекарств*\n"

            text += "\n"

        text += "**Нелекарственные рекомендации:**\n"
        text += "• Обильное теплое питье (чай с медом, компот)\n"
        text += "• Полоскание горла солевым раствором (1 ч.л. соли на стакан воды)\n"
        text += "• Отдых и покой\n"
        text += "• Увлажнение воздуха в помещении\n\n"

        text += "**Важные указания:**\n"
        text += "• Проконсультируйтесь с врачом перед применением\n"
        text += "• Соблюдайте дозировку\n"
        text += "• При ухудшении состояния обратитесь за помощью\n\n"

        text += "**Это предварительные рекомендации. Для точного лечения обратитесь к врачу.**"

        return text

    async def process(self, state: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
        diagnosis_data = self._extract_diagnosis_data(state)
        diagnosis_text = self._get_diagnosis_text(diagnosis_data)

        logger.info(f"MedicineProvider запущен...")
        logger.info(f"   Диагноз: {diagnosis_text}")
        logger.info(f"   Тип состояния: {type(state)}")

        if not diagnosis_text:
            logger.warning("   Текст диагноза не найден, пробуем альтернативные способы")
            if isinstance(state, dict):
                diagnosis_text = state.get('diagnosis', '')
            elif hasattr(state, 'diagnosis'):
                diagnosis_text = getattr(state, 'diagnosis', '')

        if not diagnosis_text or diagnosis_text.lower() == 'неизвестно':
            logger.error("Не предоставлен диагноз для подбора лекарств")
            return self._empty_result("Нет диагноза для подбора лекарств")

        symptoms = self._extract_symptoms(state)
        logger.info(f"   Симптомы: {symptoms[:3]}...")

        contraindications = self._extract_contraindications(state)
        logger.info(f"   Противопоказания: {contraindications}")

        relevant_medicines = self._find_relevant_medicines(diagnosis_text, symptoms)

        recommendations = await self._get_llm_recommendations_with_contraindications(
            diagnosis_text, symptoms, relevant_medicines, contraindications, state
        )

        recommendations_text = self._format_recommendations_text(
            recommendations, diagnosis_text, contraindications
        )

        result = {
            "suggested_medicines": recommendations,
            "database_medicines_found": len(relevant_medicines),
            "recommendation_success": len(recommendations) > 0,
            "diagnosis": diagnosis_text,
            "medicines_count": len(recommendations),
            "used_database": len(relevant_medicines) > 0,
            "used_llm": any(r.get('is_from_llm', False) for r in recommendations),
            "contraindications_considered": bool(contraindications),
            "recommendations_text": recommendations_text,
            "has_recommendations": True
        }

        logger.info(f"MedicineProvider вернул {len(recommendations)} рекомендаций")
        logger.info(f"   Использован LLM: {result['used_llm']}")
        logger.info(f"   Учтены противопоказания: {result['contraindications_considered']}")

        return result

    def _extract_contraindications(self, state: Any) -> Dict[str, Any]:
        contraindications = {}

        if hasattr(state, 'contraindications'):
            contra_obj = getattr(state, 'contraindications')
            if hasattr(contra_obj, 'to_dict'):
                contraindications = contra_obj.to_dict()
            elif isinstance(contra_obj, dict):
                contraindications = contra_obj
            elif hasattr(contra_obj, '__dict__'):
                contraindications = contra_obj.__dict__

        elif hasattr(state, 'user_profile'):
            profile = getattr(state, 'user_profile')
            if hasattr(profile, 'to_dict'):
                profile_dict = profile.to_dict()
                contraindications = {
                    'allergies': profile_dict.get('allergies', []),
                    'chronic_conditions': profile_dict.get('chronic_conditions', []),
                    'current_medications': profile_dict.get('current_medications', []),
                    'pregnancy': profile_dict.get('pregnancy'),
                    'breastfeeding': profile_dict.get('breastfeeding')
                }

        elif isinstance(state, dict):
            contraindications = state.get('contraindications', {})

        return contraindications

    def _find_relevant_medicines(self, diagnosis: str, symptoms: List[str]) -> List[Dict]:
        if not self.medicine_db:
            logger.warning("База данных лекарств пуста")
            return []

        relevant = []
        diagnosis_lower = diagnosis.lower()

        search_terms = []

        if any(word in diagnosis_lower for word in ['фарингит', 'тонзиллит', 'ангин', 'горл']):
            search_terms.extend(['горло', 'горл', 'фарингит', 'тонзиллит', 'ангин', 'антибиотик', 'антисептик'])

        if any(word in diagnosis_lower for word in ['орви', 'грипп', 'простуд']):
            search_terms.extend(['орви', 'грипп', 'простуд', 'температура', 'жаропонижающее'])

        if any(word in diagnosis_lower for word in ['кашель', 'бронхит']):
            search_terms.extend(['кашель', 'бронхит', 'отхаркивающее', 'мокрота'])

        search_terms.extend(diagnosis_lower.split())

        for symptom in symptoms[:3]:
            symptom_lower = symptom.lower()
            search_terms.extend(symptom_lower.split())

        stop_words = ['и', 'в', 'на', 'с', 'у', 'по', 'для', 'от', 'о', 'что', 'как', 'уже', 'еще']
        search_terms = [term for term in search_terms
                        if term not in stop_words and len(term) > 2]
        search_terms = list(set(search_terms))

        logger.info(f"Поиск лекарств по ключевым словам: {search_terms}")
        logger.info(f"   База данных: {len(self.medicine_db)} лекарств")

        for medicine in self.medicine_db:
            score = 0
            matches = []

            name_ru = medicine.get('name_ru', '').lower()
            if name_ru:
                for term in search_terms:
                    if term in name_ru:
                        score += 20
                        matches.append(f"название: {term}")

            uses_ru = medicine.get('uses_ru', [])
            if isinstance(uses_ru, list):
                for use in uses_ru:
                    use_lower = use.lower()
                    for term in search_terms:
                        if term in use_lower:
                            score += 50
                            matches.append(f"показание: {term}")

            therapeutic_class = medicine.get('therapeutic_class_ru', '').lower()
            for term in search_terms:
                if term in therapeutic_class:
                    score += 30
                    matches.append(f"класс: {term}")

            if score > 40:
                medicine_copy = medicine.copy()
                medicine_copy['relevance_score'] = score
                medicine_copy['match_reasons'] = matches[:3]
                relevant.append(medicine_copy)
                logger.debug(f"   Найдено: {medicine.get('name_ru')} - балл: {score}")

        relevant.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        logger.info(f"Найдено релевантных лекарств: {len(relevant)}")

        if relevant:
            logger.info(f"   Топ-3: {[med.get('name_ru') for med in relevant[:3]]}")

        return relevant[:5]

    async def _get_llm_recommendations_with_contraindications(
            self,
            diagnosis: str,
            symptoms: List[str],
            relevant_medicines: List[Dict],
            contraindications: Dict,
            state: Any
    ) -> List[Dict]:
        logger.info(f"🤖 Запрос к LLM для рекомендаций с учетом противопоказаний: {diagnosis}")

        symptoms_text = ", ".join(symptoms[:5]) if symptoms else "симптомы не указаны"

        contraindications_text = self._format_contraindications_for_prompt(contraindications)

        medicines_info = self._format_medicines_for_prompt(relevant_medicines[:10])

        prompt = f"""Ты - опытный врач-фармацевт. Подбери безопасные лекарства для пациента с учетом противопоказаний.

ДИАГНОЗ: {diagnosis}
СИМПТОМЫ: {symptoms_text}

ПРОТИВОПОКАЗАНИЯ пациента (УЧТИ ИХ!):
{contraindications_text}

ЛЕКАРСТВА из базы данных (можешь использовать как справочную информацию):
{medicines_info if medicines_info else 'Нет данных в базе'}

ИНСТРУКЦИИ:
1. Подбери 2-3 самых подходящих лекарства для этого диагноза
2. УЧТИ все противопоказания пациента - НЕ рекомендую то, что нельзя!
3. Если у пациента аллергия на пенициллин - НЕ рекомендую антибиотики пенициллинового ряда
4. Если беременность/лактация - выбирай максимально безопасные препараты
5. Если проблемы с печенью/почками - осторожно с дозировками
6. Для каждого лекарства укажи:
   - Название (на русском)
   - Почему именно это лекарство подходит
   - Конкретную дозировку для взрослого
   - Особые меры предосторожности с учетом противопоказаний
   - Альтернативы (если есть)

ОТВЕЧАЙ ТОЛЬКО В ФОРМАТЕ JSON:

{{
    "recommendations": [
        {{
            "name": "Название лекарства",
            "reason": "Почему подходит для этого диагноза",
            "dosage": "Конкретная дозировка (например: 500 мг 3 раза в день)",
            "precautions": "Особые меры с учетом противопоказаний пациента",
            "alternatives": ["Альтернатива 1", "Альтернатива 2"]
        }}
    ]
}}"""

        try:
            response = await self.generate_with_llm(
                prompt=prompt,
                system_prompt="""Ты - опытный врач-фармацевт. 
                Твои рекомендации должны быть:
                1. Безопасными с учетом всех противопоказаний
                2. Конкретными и практичными
                3. На русском языке
                4. С указанием точных дозировок
                5. С предупреждениями о возможных рисках

                Если есть серьезные противопоказания, лучше порекомендовать консультацию врача.
                Отвечай ТОЛЬКО в указанном JSON формате.""",
                max_tokens=1000
            )

            if response:
                recommendations = self._parse_llm_response(response)
                if recommendations:
                    for rec in recommendations:
                        rec['is_from_llm'] = True

                    logger.info(f"LLM сгенерировал {len(recommendations)} рекомендаций")

                    safe_recommendations = self._check_recommendations_safety(
                        recommendations, contraindications
                    )

                    return safe_recommendations

        except Exception as e:
            logger.error(f"Ошибка при запросе рекомендаций к LLM: {e}")

        logger.warning("LLM не сработал, используем простые рекомендации с проверкой безопасности")
        simple_recommendations = self._create_simple_recommendations(diagnosis, symptoms)

        safe_recommendations = self._check_recommendations_safety(
            simple_recommendations, contraindications
        )

        return safe_recommendations

    def _format_contraindications_for_prompt(self, contraindications: Dict) -> str:
        if not contraindications:
            return "Противопоказаний не указано"

        lines = []

        allergies = contraindications.get('allergies')
        if allergies:
            if isinstance(allergies, list):
                lines.append(f"• Аллергии: {', '.join(allergies)}")
            elif allergies != 'нет':
                lines.append(f"• Аллергии: {allergies}")

        chronic = contraindications.get('chronic_conditions')
        if chronic:
            if isinstance(chronic, list):
                lines.append(f"• Хронические заболевания: {', '.join(chronic)}")
            elif chronic != 'нет':
                lines.append(f"• Хронические заболевания: {chronic}")

        medications = contraindications.get('current_medications')
        if medications:
            if isinstance(medications, list):
                lines.append(f"• Текущие лекарства: {', '.join(medications)}")
            elif medications != 'нет':
                lines.append(f"• Текущие лекарства: {medications}")

        if contraindications.get('pregnancy'):
            lines.append("• Беременность: ДА")
        if contraindications.get('breastfeeding'):
            lines.append("• Грудное вскармливание: ДА")

        if contraindications.get('kidney_problems'):
            lines.append("• Проблемы с почками: ДА")
        if contraindications.get('liver_problems'):
            lines.append("• Проблемы с печенью: ДА")

        other = contraindications.get('other_restrictions', [])
        if other:
            lines.append(f"• Другие ограничения: {', '.join(other)}")

        return "\n".join(lines) if lines else "Противопоказаний не указано"

    def _format_medicines_for_prompt(self, medicines: List[Dict]) -> str:
        if not medicines:
            return ""

        lines = []
        for i, med in enumerate(medicines[:5], 1):
            name = med.get('name_ru', med.get('name_en', 'Неизвестно'))
            uses = med.get('uses_ru', med.get('uses_en', []))
            therapeutic_class = med.get('therapeutic_class_ru', med.get('therapeutic_class_en', ''))
            form = med.get('form', '')

            lines.append(f"{i}. {name}")
            if therapeutic_class:
                lines.append(f"   Класс: {therapeutic_class}")
            if uses:
                lines.append(f"   Показания: {', '.join(uses[:2])}")
            if form:
                lines.append(f"   Форма: {form}")
            lines.append("")

        return "\n".join(lines)

    def _parse_llm_response(self, response: str) -> List[Dict]:
        try:
            import re

            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                recommendations = data.get('recommendations', [])

                valid_recommendations = []
                for rec in recommendations:
                    if isinstance(rec, dict) and rec.get('name'):
                        valid_rec = {
                            'name': rec.get('name', ''),
                            'reason': rec.get('reason', 'Для лечения указанного заболевания'),
                            'dosage': rec.get('dosage', 'По назначению врача'),
                            'precautions': rec.get('precautions', 'Проконсультируйтесь с врачом'),
                            'alternatives': rec.get('alternatives', []),
                            'is_from_llm': True
                        }
                        valid_recommendations.append(valid_rec)

                return valid_recommendations[:3]

        except Exception as e:
            logger.error(f"Ошибка парсинга ответа LLM: {e}")

        return []

    def _check_recommendations_safety(self, recommendations: List[Dict], contraindications: Dict) -> List[Dict]:
        if not contraindications or not recommendations:
            return recommendations

        safe_recommendations = []

        for rec in recommendations:
            medicine_name = rec.get('name', '').lower()
            is_safe = True
            warnings = []

            if contraindications.get('allergies'):
                allergies = contraindications['allergies']
                if isinstance(allergies, str) and 'пенициллин' in allergies.lower():
                    if any(word in medicine_name for word in ['амоксициллин', 'аугментин', 'амоксиклав', 'пенициллин']):
                        is_safe = False
                        warnings.append("СОДЕРЖИТ ПЕНИЦИЛЛИН - ПРОТИВОПОКАЗАНО!")

            if contraindications.get('pregnancy'):
                if any(word in medicine_name for word in ['тетрациклин', 'доксициклин', 'рифампицин', 'варфарин']):
                    warnings.append("ОСТОРОЖНО: не рекомендуется при беременности")

            if contraindications.get('liver_problems'):
                if 'парацетамол' in medicine_name:
                    warnings.append("ОСТОРОЖНО: при проблемах с печенью дозу парацетамола нужно уменьшать")

            if contraindications.get('kidney_problems'):
                if any(word in medicine_name for word in ['ибупрофен', 'диклофенак', 'напроксен']):
                    warnings.append("ОСТОРОЖНО: НПВП могут ухудшать функцию почек")

            if is_safe:
                if warnings:
                    current_precautions = rec.get('precautions', '')
                    extra_warnings = " ".join(warnings)
                    rec['precautions'] = f"{current_precautions} {extra_warnings}".strip()

                safe_recommendations.append(rec)
            else:
                logger.warning(f"Исключили лекарство {medicine_name} из-за противопоказаний")

        return safe_recommendations

    def _create_simple_recommendations(self, diagnosis: str, symptoms: List[str]) -> List[Dict]:
        diagnosis_lower = diagnosis.lower()

        if any(word in diagnosis_lower for word in ['фарингит', 'тонзиллит', 'ангин', 'горл']):
            return [
                {
                    "name": "Парацетамол",
                    "reason": "Для снижения температуры и боли в горле",
                    "dosage": "500 мг 3-4 раза в день (максимум 4 г в сутки)",
                    "precautions": "Не превышать суточную дозу, осторожно при проблемах с печенью",
                    "alternatives": ["Ибупрофен", "Аспирин"]
                },
                {
                    "name": "Граммидин",
                    "reason": "Местное лечение боли в горле, антисептическое действие",
                    "dosage": "1 таблетка 3-4 раза в день, рассасывать после еды",
                    "precautions": "После приема не пить и не есть 30 минут",
                    "alternatives": ["Стрепсилс", "Фарингосепт", "Лизобакт"]
                }
            ]

        elif any(word in diagnosis_lower for word in ['грипп', 'орви', 'простуд']):
            return [
                {
                    "name": "Парацетамол",
                    "reason": "Жаропонижающее и обезболивающее при температуре",
                    "dosage": "500 мг каждые 6-8 часов при температуре выше 38.5°C",
                    "precautions": "Не сочетать с алкоголем, осторожно при проблемах с печенью",
                    "alternatives": ["Ибупрофен"]
                },
                {
                    "name": "Аскорбиновая кислота (витамин C)",
                    "reason": "Поддержка иммунитета при вирусных инфекций",
                    "dosage": "1000 мг в сутки, разделить на 2 приема",
                    "precautions": "Принимать после еды, может вызывать раздражение желудка",
                    "alternatives": ["Комплексные витамины", "Цинк"]
                }
            ]

        return [
            {
                "name": "Парацетамол",
                "reason": "Обезболивающее и жаропонижающее средство",
                "dosage": "500 мг при необходимости, не более 4 раз в сутки",
                "precautions": "Проконсультируйтесь с врачом, осторожно при проблемах с печенью",
                "alternatives": ["Ибупрофен"]
            }
        ]

    def _get_diagnosis_text(self, diagnosis_data: Any) -> str:
        if hasattr(diagnosis_data, 'name'):
            return diagnosis_data.name

        elif isinstance(diagnosis_data, dict):
            possible_keys = ['diagnosis', 'name', 'primary_diagnosis', 'preliminary_diagnosis']
            for key in possible_keys:
                if key in diagnosis_data:
                    value = diagnosis_data[key]
                    if value:
                        if isinstance(value, dict):
                            if 'diagnosis' in value:
                                return value['diagnosis']
                            elif 'name' in value:
                                return value['name']
                        elif isinstance(value, str):
                            return value
                        elif hasattr(value, 'name'):
                            return value.name

        elif hasattr(diagnosis_data, 'primary_diagnosis'):
            primary = getattr(diagnosis_data, 'primary_diagnosis')
            if primary:
                if hasattr(primary, 'name'):
                    return primary.name
                elif isinstance(primary, dict) and 'name' in primary:
                    return primary['name']
                elif isinstance(primary, dict) and 'diagnosis' in primary:
                    return primary['diagnosis']

        elif isinstance(diagnosis_data, str):
            return diagnosis_data

        logger.warning(f"Не удалось извлечь текст диагноза из: {type(diagnosis_data)}")
        return ""

    def _extract_diagnosis_data(self, state: Any) -> Any:
        if hasattr(state, 'primary_diagnosis'):
            return getattr(state, 'primary_diagnosis')

        elif isinstance(state, dict):
            for key in ['primary_diagnosis', 'preliminary_diagnosis', 'diagnosis_data']:
                if key in state:
                    return state[key]

            if 'diagnosis' in state:
                return state['diagnosis']

        elif hasattr(state, 'get_diagnosis'):
            try:
                return state.get_diagnosis()
            except Exception as e:
                logger.warning(f"Ошибка при вызове get_diagnosis: {e}")

        elif hasattr(state, 'diagnosis'):
            return getattr(state, 'diagnosis')

        return state

    def _extract_symptoms(self, state: Any) -> List[str]:
        if hasattr(state, 'get_symptoms_for_processing'):
            try:
                symptoms = state.get_symptoms_for_processing()
                if symptoms:
                    return symptoms
            except Exception as e:
                logger.warning(f"Ошибка при вызове get_symptoms_for_processing: {e}")

        elif hasattr(state, 'symptom_texts'):
            symptom_texts = getattr(state, 'symptom_texts', [])
            if symptom_texts:
                return symptom_texts

        elif isinstance(state, dict):
            symptom_sources = [
                state.get('symptom_texts', []),
                state.get('symptoms', []),
                state.get('normalized_symptoms', []),
                [state.get('text', '')] if state.get('text') else [],
                [state.get('input', '')] if state.get('input') else []
            ]

            for source in symptom_sources:
                if source:
                    if isinstance(source, list):
                        return [str(item) for item in source if item]
                    elif isinstance(source, str) and source.strip():
                        return [source.strip()]

        elif hasattr(state, 'normalized_symptoms'):
            normalized = getattr(state, 'normalized_symptoms', [])
            if normalized:
                symptoms = []
                for item in normalized:
                    if isinstance(item, dict):
                        symptom_text = item.get('normalized', item.get('text', str(item)))
                        if symptom_text:
                            symptoms.append(symptom_text)
                    else:
                        symptoms.append(str(item))
                return symptoms

        elif isinstance(state, str) and state.strip():
            return [state.strip()]

        logger.warning(f"Не удалось извлечь симптомы из состояния типа: {type(state)}")
        return []

    def _empty_result(self, reason: str) -> Dict[str, Any]:
        return {
            "suggested_medicines": [],
            "database_medicines_found": 0,
            "recommendation_success": False,
            "diagnosis": "",
            "medicines_count": 0,
            "used_database": False,
            "used_llm": False,
            "contraindications_considered": False,
            "recommendations_text": f"Не удалось подобрать лечение: {reason}",
            "has_recommendations": False,
            "error": reason
        }

    def _create_fallback_database(self) -> List[Dict]:
        return [
            {
                "id": 1,
                "name_ru": "Парацетамол",
                "name_en": "Paracetamol",
                "uses_ru": ["Боль", "Лихорадка", "Температура", "Головная боль"],
                "therapeutic_class_ru": "Жаропонижающие и обезболивающие",
                "form": "таблетки",
                "side_effects_ru": ["Тошнота", "Боль в животе", "Аллергические реакции"],
                "substitutes_ru": ["Ибупрофен", "Аспирин"]
            },
            {
                "id": 2,
                "name_ru": "Ибупрофен",
                "name_en": "Ibuprofen",
                "uses_ru": ["Боль", "Воспаление", "Температура", "Артрит"],
                "therapeutic_class_ru": "Нестероидные противовоспалительные средства",
                "form": "таблетки",
                "side_effects_ru": ["Изжога", "Боль в желудке", "Головокружение"],
                "substitutes_ru": ["Напроксен", "Диклофенак"]
            },
            {
                "id": 3,
                "name_ru": "Амоксициллин",
                "name_en": "Amoxicillin",
                "uses_ru": ["Бактериальные инфекции", "Ангина", "Бронхит", "Пневмония"],
                "therapeutic_class_ru": "Антибиотики пенициллинового ряда",
                "form": "таблетки",
                "side_effects_ru": ["Диарея", "Тошнота", "Аллергические реакции"],
                "substitutes_ru": ["Аугментин", "Флемоксин"],
                "contraindications": ["Аллергия на пенициллин"]
            }
        ]