from .base_agent import BaseAgent
import json
import logging
from typing import Dict, Any, List, Union, Optional
import datetime

logger = logging.getLogger(__name__)


class Diagnostician(BaseAgent):
    def __init__(self, llm_client):
        super().__init__("Diagnostician", llm_client)

    async def process(self, state: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
        symptoms_data = self._extract_symptoms_data(state)

        localizations = []
        if hasattr(state, 'localization_analysis'):
            localization_data = getattr(state, 'localization_analysis')
            if isinstance(localization_data, dict):
                localizations = localization_data.get('localizations', [])
        elif isinstance(state, dict):
            localizations = state.get('localizations', [])

        symptoms_text = self._format_symptoms_for_prompt(symptoms_data)

        if localizations:
            localization_text = f"\n\n📍 **Локализация симптомов:** {', '.join(localizations)}"
            symptoms_text += localization_text

        try:
            if not symptoms_data:
                logger.warning("No symptoms provided for diagnosis")
                return self._create_empty_diagnosis_result("Нет симптомов для анализа")

            logger.info(f"Diagnosing {len(symptoms_data)} symptoms")

            diagnosis_result = await self._get_diagnosis_from_llm(symptoms_text)

            result = {
                "preliminary_diagnosis": diagnosis_result,
                "diagnosis": diagnosis_result.get("diagnosis", ""),
                "diagnosis_data": diagnosis_result,
                "diagnosis_success": True,
                "symptoms_analyzed": len(symptoms_data),
                "diagnosis_timestamp": datetime.datetime.now().isoformat(),
                "agent": self.name
            }

            logger.info(f"Diagnostician returning: {result['preliminary_diagnosis'].get('diagnosis', 'unknown')}")
            return result
        except Exception as e:
            logger.error(f"Diagnosis failed: {e}")
            return {
                "preliminary_diagnosis": {
                    "diagnosis": "Требуется консультация врача",
                    "confidence": 0.3,
                    "needs_clarification": True
                },
                "diagnosis": "Требуется консультация врача",
                "diagnosis_success": False,
                "error": str(e)
            }

    def _extract_symptoms_data(self, state: Any) -> List[str]:
        symptoms = []

        if isinstance(state, dict):
            symptom_sources = [
                state.get("symptoms", []),
                state.get("symptom_texts", []),
                state.get("normalized_symptoms", []),
                [state.get("text", "")] if state.get("text") else [],
                [state.get("input", "")] if state.get("input") else []
            ]

            for source in symptom_sources:
                if source:
                    if isinstance(source, list):
                        symptoms.extend([str(item) for item in source if item])
                    elif isinstance(source, str) and source.strip():
                        symptoms.append(source.strip())
                    break

        elif hasattr(state, 'symptom_texts'):
            symptom_texts = getattr(state, 'symptom_texts', [])
            if symptom_texts:
                symptoms = [str(s) for s in symptom_texts if s]

        elif hasattr(state, 'normalized_symptoms'):
            normalized = getattr(state, 'normalized_symptoms', [])
            if normalized:
                for item in normalized:
                    if isinstance(item, dict):
                        symptoms.append(item.get('normalized', item.get('text', str(item))))
                    else:
                        symptoms.append(str(item))

        elif hasattr(state, 'get_symptoms_for_processing'):
            try:
                extracted = state.get_symptoms_for_processing()
                if extracted:
                    symptoms = [str(s) for s in extracted if s]
            except Exception as e:
                logger.warning(f"Failed to call get_symptoms_for_processing: {e}")

        elif hasattr(state, 'symptoms'):
            symptom_objects = getattr(state, 'symptoms', [])
            for symptom in symptom_objects:
                if hasattr(symptom, 'description'):
                    symptoms.append(symptom.description)
                elif isinstance(symptom, dict):
                    text = symptom.get('description', symptom.get('text', symptom.get('normalized', str(symptom))))
                    symptoms.append(text)
                else:
                    symptoms.append(str(symptom))

        elif isinstance(state, str) and state.strip():
            symptoms = [state.strip()]

        filtered_symptoms = [s.strip() for s in symptoms if s and str(s).strip()]

        logger.debug(f"Extracted {len(filtered_symptoms)} symptoms for diagnosis")
        return filtered_symptoms

    def _format_symptoms_for_prompt(self, symptoms: List[str]) -> str:
        if not symptoms:
            return "Симптомы не указаны"

        if len(symptoms) == 1:
            return f"Основная жалоба: {symptoms[0]}"

        formatted = "Жалобы пациента:\n"
        for i, symptom in enumerate(symptoms[:10], 1):
            formatted += f"{i}. {symptom}\n"

        if len(symptoms) > 10:
            formatted += f"... и еще {len(symptoms) - 10} симптомов\n"

        return formatted.strip()

    async def _get_diagnosis_from_llm(self, symptoms_text: str) -> Dict[str, Any]:
        prompt = self._create_diagnosis_prompt(symptoms_text)

        try:
            response = await self.generate_with_llm(
                prompt=prompt,
                system_prompt=self._get_system_prompt(),
                max_tokens=600
            )

            if not response:
                logger.warning("LLM returned empty response")
                return self._create_fallback_diagnosis(symptoms_text)

            logger.debug(f"LLM raw response type: {type(response)}")
            logger.debug(f"LLM raw response (first 500 chars): {str(response)[:500]}")

            diagnosis_result = self._parse_and_validate_llm_response(response)
            return diagnosis_result

        except Exception as e:
            logger.error(f"LLM diagnosis failed: {e}", exc_info=True)
            return self._create_fallback_diagnosis(symptoms_text)

    def _create_enhanced_fallback_diagnosis(self, symptoms_text: str) -> Dict[str, Any]:
        symptoms_lower = symptoms_text.lower()

        if any(word in symptoms_lower for word in ['горл', 'боль в горл', 'ангин', 'першит']):
            if 'температур' in symptoms_lower and 'кашель' in symptoms_lower:
                diagnosis = "Острый фарингит или тонзиллит с катаральными явлениями"
                confidence = 0.75
            else:
                diagnosis = "Острый фарингит"
                confidence = 0.7

        elif any(word in symptoms_lower for word in ['голов', 'мигрен', 'головн']):
            diagnosis = "Головная боль напряжения"
            confidence = 0.65

        elif any(word in symptoms_lower for word in ['живот', 'болит живот', 'тошнот']):
            diagnosis = "Острый гастроэнтерит"
            confidence = 0.7

        elif 'температур' in symptoms_lower and ('насморк' in symptoms_lower or 'сопл' in symptoms_lower):
            diagnosis = "Острая респираторная вирусная инфекция (ОРВИ)"
            confidence = 0.8

        else:
            diagnosis = "Простудное заболевание"
            confidence = 0.6

        return {
            "diagnosis": diagnosis,
            "confidence": confidence,
            "needs_clarification": confidence < 0.7,
            "differential_diagnosis": ["Рекомендуется консультация врача для уточнения"],
            "supporting_evidence": ["Описаные пациентом симптомы"],
            "recommended_next_steps": [
                "Консультация терапевта",
                "При ухудшении состояния - вызов скорой помощи",
                "Соблюдение постельного режима"
            ]
        }

    def _create_diagnosis_prompt(self, symptoms: str) -> str:
        return f"""Ты - опытный врач - диагност.Проанализируй симптомы и поставь предварительный диагноз.

    {symptoms}

    ИНСТРУКЦИИ:
    1.Поставь ТОЧНЫЙ медицинский диагноз на русском языке
    2.Оцени уверенность от 0.0 до 1.0 (1.0 - абсолютная уверенность)
    3.Укажи, нужны ли дополнительные уточнения (true / false) если оценка уверенности ниже 0.7 - используй строчные true / false
    4.Перечисли 2-3 возможных дифференциальных диагноза
    5.Укажи ключевые симптомы, подтверждающие диагноз
    6.Будь клинически обоснованным и осторожным

    ВАЖНО: 
    - Ответь ТОЛЬКО в формате JSON без дополнительного текста
    - Используй true / false в нижнем регистре для булевых значений
    - Не используй True / False с заглавной буквы

    ФОРМАТ JSON:
    {{
        "diagnosis": "НАЗВАНИЕ ДИАГНОЗА",
        "confidence": 0.85,
        "needs_clarification": false,
        "differential_diagnosis": ["диагноз1", "диагноз2"],
        "supporting_evidence": ["симптом1", "симптом2"],
        "recommended_next_steps": ["шаг1", "шаг2"]
    }}

    ПРИМЕР:
    {{
        "diagnosis": "Острая респираторная вирусная инфекция (ОРВИ)",
        "confidence": 0.82,
        "needs_clarification": false,
        "differential_diagnosis": ["Грипп", "Бактериальный фарингит"],
        "supporting_evidence": ["температура", "насморк", "боль в горле"],
        "recommended_next_steps": ["Отдых", "Обильное питье", "Консультация врача"]
    }}"""

    def _get_system_prompt(self) -> str:
        return """Ты - врач-терапевт с 20-летним клиническим опытом.
        Твои задачи:
        1. Ставить клинически обоснованные диагнозы
        2. Использовать стандартную медицинскую терминологию
        3. Быть консервативным в оценке уверенности
        4. При недостатке информации указывать needs_clarification: true
        5. Всегда рекомендовать консультацию врача
        6. Отвечать ТОЛЬКО в указанном JSON формате

        Будь профессиональным, точным и заботливым."""

    def _parse_and_validate_llm_response(self, response: str) -> Dict[str, Any]:
        self.logger.debug(f"Starting parse of response, type: {type(response)}")

        if isinstance(response, dict):
            self.logger.debug("Response is already a dict")
            return self._validate_and_normalize_diagnosis(response)

        if not isinstance(response, str):
            self.logger.error(f"Expected string but got: {type(response)}")
            return self._create_fallback_diagnosis("")

        response = response.strip()
        self.logger.debug(f"Response to parse (first 200 chars): {response[:200]}")

        try:
            cleaned_response = self._clean_json_response(response)

            data = json.loads(cleaned_response)

            if "preliminary_diagnosis" in data:
                return self._validate_and_normalize_diagnosis(data["preliminary_diagnosis"])
            else:
                return self._validate_and_normalize_diagnosis(data)

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")

            try:
                fixed_response = self._fix_common_json_errors(response)
                data = json.loads(fixed_response)

                if "preliminary_diagnosis" in data:
                    return self._validate_and_normalize_diagnosis(data["preliminary_diagnosis"])
                else:
                    return self._validate_and_normalize_diagnosis(data)

            except Exception as e2:
                self.logger.error(f"Failed even after fixing: {e2}")

                try:
                    import re
                    json_match = re.search(r'\{[^{}]*\}|\{[^{}]*\{[^{}]*\}[^{}]*\}', response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                        json_str = json_str.replace('True', 'true').replace('False', 'false')
                        data = json.loads(json_str)

                        if "preliminary_diagnosis" in data:
                            return self._validate_and_normalize_diagnosis(data["preliminary_diagnosis"])
                        else:
                            return self._validate_and_normalize_diagnosis(data)

                except Exception as e3:
                    self.logger.error(f"Failed to extract JSON: {e3}")

        self.logger.warning("All JSON parsing strategies failed, using fallback")
        return self._create_fallback_diagnosis("")

    def _clean_json_response(self, response: str) -> str:
        lines = response.split('\n')
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped:
                stripped = stripped.replace('True', 'true').replace('False', 'false')
                cleaned_lines.append(stripped)

        return ' '.join(cleaned_lines)

    def _fix_common_json_errors(self, response: str) -> str:
        response = response.replace('True', 'true').replace('False', 'false')

        response = response.replace('None', 'null')

        import re
        response = re.sub(r',\s*}', '}', response)
        response = re.sub(r',\s*]', ']', response)

        response = response.replace("'", '"')

        return response

    def _create_fallback_diagnosis_from_text(self, response_text: str) -> Dict[str, Any]:
        diagnosis = "Требуется консультация врача"

        lines = response_text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if 'диагноз' in line_lower and ':' in line:
                parts = line.split(':', 1)
                if len(parts) > 1:
                    potential_diag = parts[1].strip()
                    if len(potential_diag) > 5:
                        diagnosis = potential_diag
                        break

        return {
            "diagnosis": diagnosis,
            "confidence": 0.6,
            "needs_clarification": True,
            "differential_diagnosis": ["Требуется дифференциальная диагностика"],
            "supporting_evidence": [],
            "recommended_next_steps": ["Консультация врача"]
        }

    def _extract_json_string(self, response: str) -> Optional[str]:
        if '```json' in response:
            parts = response.split('```json')
            if len(parts) > 1:
                json_part = parts[1].split('```')[0].strip()
                return json_part

        elif '```' in response:
            parts = response.split('```')
            if len(parts) > 1:
                json_part = parts[1].strip()
                if json_part.startswith('json'):
                    json_part = json_part[4:].strip()
                return json_part

        start_idx = response.find('{')
        end_idx = response.rfind('}')

        if start_idx != -1 and end_idx > start_idx:
            json_str = response[start_idx:end_idx + 1]

            if '"diagnosis"' in json_str or "'diagnosis'" in json_str:
                return json_str

        if response.startswith('{') and response.endswith('}'):
            return response

        return None

    def _validate_and_normalize_diagnosis(self, diagnosis_data: Dict) -> Dict[str, Any]:
        result = {
            "diagnosis": "",
            "confidence": 0.5,
            "needs_clarification": True,
            "differential_diagnosis": [],
            "supporting_evidence": [],
            "recommended_next_steps": []
        }

        diagnosis_text = ""
        if "diagnosis" in diagnosis_data:
            diagnosis_text = str(diagnosis_data["diagnosis"]).strip()

        if not diagnosis_text or len(diagnosis_text) < 2:
            diagnosis_text = "Требуется дополнительное обследование"

        result["diagnosis"] = diagnosis_text

        confidence = 0.5
        if "confidence" in diagnosis_data:
            try:
                conf = float(diagnosis_data["confidence"])
                confidence = max(0.0, min(1.0, conf))
            except (ValueError, TypeError):
                pass

        result["confidence"] = round(confidence, 2)

        needs_clarification = True
        if "needs_clarification" in diagnosis_data:
            needs_clarification = bool(diagnosis_data["needs_clarification"])

        result["needs_clarification"] = needs_clarification

        differential = []
        if "differential_diagnosis" in diagnosis_data:
            diff_data = diagnosis_data["differential_diagnosis"]
            if isinstance(diff_data, list):
                for item in diff_data[:3]:
                    if item and str(item).strip():
                        differential.append(str(item).strip())

        result["differential_diagnosis"] = differential

        evidence = []
        if "supporting_evidence" in diagnosis_data:
            evidence_data = diagnosis_data["supporting_evidence"]
            if isinstance(evidence_data, list):
                for item in evidence_data[:5]:
                    if item and str(item).strip():
                        evidence.append(str(item).strip())

        result["supporting_evidence"] = evidence

        next_steps = []
        if "recommended_next_steps" in diagnosis_data:
            steps_data = diagnosis_data["recommended_next_steps"]
            if isinstance(steps_data, list):
                for item in steps_data[:3]:
                    if item and str(item).strip():
                        next_steps.append(str(item).strip())

        if not next_steps:
            next_steps = [
                "Консультация врача для подтверждения диагноза",
                "Соблюдение рекомендаций по лечению",
                "Обращение за помощью при ухудшении состояния"
            ]

        result["recommended_next_steps"] = next_steps

        if len(result["diagnosis"]) > 300:
            result["diagnosis"] = result["diagnosis"][:300] + "..."

        if result["confidence"] < 0.3:
            result["needs_clarification"] = True

        return result

    def _create_fallback_diagnosis(self, symptoms_text: str) -> Dict[str, Any]:
        symptoms_lower = symptoms_text.lower()

        diagnosis = "Требуется очный осмотр врача"
        confidence = 0.3
        needs_clarification = True

        if any(word in symptoms_lower for word in ['голов', 'мигрен', 'головн']):
            diagnosis = "Головная боль напряжения"
            confidence = 0.6
            if 'температур' in symptoms_lower:
                diagnosis = "ОРВИ с головной болью"
                confidence = 0.7

        elif any(word in symptoms_lower for word in ['горл', 'боль в горл', 'ангин']):
            diagnosis = "Острый фарингит"
            confidence = 0.65
            if 'температур' in symptoms_lower and 'гной' in symptoms_lower:
                diagnosis = "Острый тонзиллит (ангина)"
                confidence = 0.75

        elif any(word in symptoms_lower for word in ['живот', 'болит живот', 'тошнот', 'рвот']):
            diagnosis = "Острый гастроэнтерит"
            confidence = 0.7

        elif any(word in symptoms_lower for word in ['кашель', 'кашл', 'мокрот']):
            diagnosis = "Острый бронхит"
            confidence = 0.65
            if 'температур' in symptoms_lower and 'одышк' in symptoms_lower:
                diagnosis = "Острая респираторная инфекция"
                confidence = 0.7

        elif 'температур' in symptoms_lower and ('насморк' in symptoms_lower or 'сопл' in symptoms_lower):
            diagnosis = "Острая респираторная вирусная инфекция (ОРВИ)"
            confidence = 0.8

        return {
            "diagnosis": diagnosis,
            "confidence": confidence,
            "needs_clarification": needs_clarification,
            "differential_diagnosis": ["Требуется дифференциальная диагностика"],
            "supporting_evidence": ["Симптомы пациента"],
            "recommended_next_steps": [
                "Консультация терапевта",
                "Лабораторное обследование при необходимости",
                "Наблюдение за динамикой состояния"
            ]
        }

    def _create_empty_diagnosis_result(self, reason: str) -> Dict[str, Any]:
        return {
            "preliminary_diagnosis": {
                "diagnosis": f"Диагноз не поставлен: {reason}",
                "confidence": 0.0,
                "needs_clarification": True,
                "differential_diagnosis": [],
                "supporting_evidence": [],
                "recommended_next_steps": ["Опишите симптомы более подробно"]
            },
            "diagnosis_success": False,
            "symptoms_analyzed": 0,
            "diagnosis_timestamp": datetime.datetime.now().isoformat(),
            "agent": self.name,
            "error": reason
        }

    def _create_error_diagnosis_result(self, error: str) -> Dict[str, Any]:
        return {
            "preliminary_diagnosis": {
                "diagnosis": f"Ошибка диагностики: {error[:100]}",
                "confidence": 0.0,
                "needs_clarification": True,
                "differential_diagnosis": [],
                "supporting_evidence": [],
                "recommended_next_steps": ["Попробуйте еще раз", "Обратитесь к врачу"]
            },
            "diagnosis_success": False,
            "symptoms_analyzed": 0,
            "diagnosis_timestamp": datetime.datetime.now().isoformat(),
            "agent": self.name,
            "error": error
        }

    async def __call__(self, state: Any) -> Dict[str, Any]:
        try:
            result = await self.process(state)
            logger.debug(f"Diagnostician completed successfully")
            return result
        except Exception as e:
            logger.error(f"Diagnostician call failed: {e}", exc_info=True)
            return self._create_error_diagnosis_result(str(e))