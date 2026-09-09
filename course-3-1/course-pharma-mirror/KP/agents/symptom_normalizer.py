from .base_agent import BaseAgent
import json
import re
import logging
from typing import Dict, Any, List, Union
import datetime
logger = logging.getLogger(__name__)


class SymptomNormalizer(BaseAgent):
    def __init__(self, llm_client):
        super().__init__("SymptomNormalizer", llm_client)

    async def process(self, state: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
        raw_symptoms = self._extract_symptoms_from_state(state)

        if not raw_symptoms:
            logger.warning("No symptoms to normalize, returning empty result")
            return {
                "normalized_symptoms": [],
                "symptom_categories": {},
                "normalization_success": False,
                "error": "No symptoms found"
            }

        logger.info(f"Normalizing {len(raw_symptoms)} symptoms: {raw_symptoms[:3]}...")

        try:
            normalized = await self._normalize_with_llm(raw_symptoms)

            result = {
                "normalized_symptoms": normalized.get("symptoms", []),
                "symptom_categories": normalized.get("categories", {}),
                "normalization_success": True,
                "raw_symptoms_count": len(raw_symptoms),
                "normalized_symptoms_count": len(normalized.get("symptoms", []))
            }

            logger.info(
                f"Successfully normalized {len(raw_symptoms)} symptoms into {len(result['normalized_symptoms'])} structured symptoms")
            return result

        except Exception as e:
            logger.error(f"Symptom normalization failed: {e}")

            fallback_result = self._default_normalization(raw_symptoms)
            return {
                "normalized_symptoms": fallback_result["symptoms"],
                "symptom_categories": fallback_result["categories"],
                "normalization_success": False,
                "error": str(e),
                "raw_symptoms_count": len(raw_symptoms),
                "normalized_symptoms_count": len(fallback_result["symptoms"])
            }

    def _extract_symptoms_from_state(self, state: Any) -> List[str]:
        symptoms = []

        if isinstance(state, dict):
            possible_keys = ['symptoms', 'symptom_texts', 'symptom_text', 'input', 'text']
            for key in possible_keys:
                if key in state:
                    value = state[key]
                    if value:
                        if isinstance(value, list):
                            symptoms.extend([str(item) for item in value])
                        elif isinstance(value, str):
                            symptoms.append(value)
                        break

        elif hasattr(state, 'symptom_texts'):
            symptom_texts = getattr(state, 'symptom_texts', [])
            if symptom_texts:
                symptoms = [str(s) for s in symptom_texts]

        elif hasattr(state, 'symptoms'):
            symptom_objects = getattr(state, 'symptoms', [])
            for symptom in symptom_objects:
                if hasattr(symptom, 'description'):
                    symptoms.append(symptom.description)
                elif isinstance(symptom, dict):
                    symptoms.append(symptom.get('description', str(symptom)))
                else:
                    symptoms.append(str(symptom))

        elif hasattr(state, 'get_symptoms_for_processing'):
            try:
                symptoms = state.get_symptoms_for_processing()
            except Exception as e:
                logger.warning(f"Failed to call get_symptoms_for_processing: {e}")

        elif hasattr(state, 'get_normalized_symptoms'):
            try:
                symptoms = state.get_normalized_symptoms()
            except Exception as e:
                logger.warning(f"Failed to call get_normalized_symptoms: {e}")

        elif hasattr(state, 'text'):
            symptoms = [str(getattr(state, 'text'))]

        elif isinstance(state, str):
            symptoms = [state]

        filtered_symptoms = [s.strip() for s in symptoms if s and str(s).strip()]

        if not filtered_symptoms:
            logger.debug(f"No symptoms extracted from state of type: {type(state)}")
        else:
            logger.debug(f"Extracted {len(filtered_symptoms)} symptoms from state")

        return filtered_symptoms

    async def _normalize_with_llm(self, raw_symptoms: List[str]) -> Dict[str, Any]:
        if len(raw_symptoms) == 1:
            symptoms_text = f"Симптом: {raw_symptoms[0]}"
        else:
            symptoms_text = "Симптомы:\n" + "\n".join([f"- {symptom}" for symptom in raw_symptoms])

        prompt = f"""Ты - медицинский регистратор. Нормализуй и структурируй симптомы пациента.

{symptoms_text}

ИНСТРУКЦИИ:
1. Нормализуй каждый симптом в стандартную медицинскую форму
2. Определи локализацию (если указана)
3. Оцени интенсивность (low/medium/high)
4. Определи длительность (acute/chronic/unknown)
5. Укажи систему организма
6. ВСЕГДА отвечай ТОЛЬКО JSON без дополнительного текста

ФОРМАТ ОТВЕТА (JSON):
{{
    "symptoms": [
        {{
            "original_text": "исходный текст",
            "normalized": "нормализованный текст (ОДНА строка)",
            "location": "локализация или null",
            "intensity": "low/medium/high",
            "duration": "acute/chronic/unknown",
            "system": "система организма"
        }}
    ],
    "categories": {{
        "system_name": ["симптом1", "симптом2"]
    }}
}}

ПРИМЕР:
{{
    "symptoms": [
        {{
            "original_text": "болит голова в висках",
            "normalized": "головная боль в височной области",
            "location": "виски",
            "intensity": "medium",
            "duration": "acute",
            "system": "neurological"
        }}
    ],
    "categories": {{
        "neurological": ["головная боль в височной области"]
    }}
}}"""

        try:
            response = await self.generate_with_llm(
                prompt=prompt,
                system_prompt="""Ты - опытный медицинский регистратор.
                Отвечай ТОЛЬКО на русском языке.
                ВСЕГДА возвращай строго указанный JSON формат.
                Не добавляй никаких пояснений, комментариев или приветствий.
                Поле "normalized" должно быть ОДНОЙ строкой.""",
                max_tokens=800
            )

            if not response:
                logger.warning("LLM returned empty response")
                return self._default_normalization(raw_symptoms)

            normalized_data = self._extract_and_validate_json(response, raw_symptoms)
            return normalized_data

        except Exception as e:
            logger.error(f"LLM normalization failed: {e}")
            raise

    def _extract_and_validate_json(self, response: str, original_symptoms: List[str]) -> Dict[str, Any]:
        response = response.strip()

        json_str = None

        if '```json' in response:
            parts = response.split('```json')
            if len(parts) > 1:
                json_str = parts[1].split('```')[0].strip()

        elif '```' in response:
            parts = response.split('```')
            if len(parts) > 1:
                json_str = parts[1].strip()
                if json_str.startswith('json'):
                    json_str = json_str[4:].strip()

        if not json_str:
            json_pattern = r'\{[\s\S]*\}'
            matches = re.findall(json_pattern, response)
            for match in matches:
                if '"symptoms"' in match or "'symptoms'" in match:
                    json_str = match
                    break

        if not json_str:
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx + 1]

        if not json_str:
            json_str = response

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.debug(f"Problematic JSON string: {json_str[:200]}...")
            return self._default_normalization(original_symptoms)

        return self._validate_normalization_structure(data, original_symptoms)

    def _validate_normalization_structure(self, data: Dict, original_symptoms: List[str]) -> Dict[str, Any]:
        result = {
            "symptoms": [],
            "categories": {}
        }

        if "symptoms" in data and isinstance(data["symptoms"], list):
            for i, symptom in enumerate(data["symptoms"]):
                if isinstance(symptom, dict):
                    valid_symptom = {
                        "original_text": symptom.get("original_text",
                                                     symptom.get("text",
                                                                 original_symptoms[i] if i < len(
                                                                     original_symptoms) else "unknown")),
                        "normalized": self._ensure_string(symptom.get("normalized", "")),
                        "location": self._ensure_string_or_none(symptom.get("location")),
                        "intensity": self._validate_intensity(symptom.get("intensity", "medium")),
                        "duration": self._validate_duration(symptom.get("duration", "unknown")),
                        "system": self._ensure_string(symptom.get("system", "general"))
                    }

                    if not valid_symptom["normalized"]:
                        valid_symptom["normalized"] = valid_symptom["original_text"]

                    result["symptoms"].append(valid_symptom)

                    system = valid_symptom["system"]
                    if system not in result["categories"]:
                        result["categories"][system] = []
                    result["categories"][system].append(valid_symptom["normalized"])

        if not result["symptoms"]:
            return self._default_normalization(original_symptoms)

        processed_texts = [s["original_text"] for s in result["symptoms"]]
        for i, original in enumerate(original_symptoms):
            if original not in processed_texts:
                symptom = {
                    "original_text": original,
                    "normalized": original,
                    "location": None,
                    "intensity": "medium",
                    "duration": "unknown",
                    "system": "general"
                }
                result["symptoms"].append(symptom)

                if "general" not in result["categories"]:
                    result["categories"]["general"] = []
                result["categories"]["general"].append(original)

        return result

    def _ensure_string(self, value: Any) -> str:
        if isinstance(value, list):
            return ", ".join(str(item) for item in value)
        return str(value) if value is not None else ""

    def _ensure_string_or_none(self, value: Any) :
        if value is None:
            return None
        if isinstance(value, list):
            return ", ".join(str(item) for item in value)
        return str(value) if str(value).strip() else None

    def _validate_intensity(self, intensity: str) -> str:
        valid_intensities = ["low", "medium", "high", "mild", "moderate", "severe"]
        intensity_lower = intensity.lower()

        intensity_map = {
            "mild": "low",
            "moderate": "medium",
            "severe": "high"
        }

        if intensity_lower in valid_intensities:
            return intensity_map.get(intensity_lower, intensity_lower)
        return "medium"

    def _validate_duration(self, duration: str) -> str:
        valid_durations = ["acute", "chronic", "unknown", "subacute"]
        duration_lower = duration.lower()

        if duration_lower in valid_durations:
            return duration_lower
        return "unknown"

    def _default_normalization(self, raw_symptoms: List[str]) -> Dict[str, Any]:
        symptoms = []
        categories = {"general": []}

        for symptom_text in raw_symptoms:
            symptom = {
                "original_text": symptom_text,
                "normalized": symptom_text,
                "location": None,
                "intensity": "medium",
                "duration": "unknown",
                "system": "general"
            }
            symptoms.append(symptom)
            categories["general"].append(symptom_text)

        return {
            "symptoms": symptoms,
            "categories": categories
        }

    async def __call__(self, state: Any) -> Dict[str, Any]:
        try:
            result = await self.process(state)

            result["agent"] = self.name
            result["timestamp"] = datetime.datetime.now().isoformat()

            return result

        except Exception as e:
            logger.error(f"SymptomNormalizer failed: {e}", exc_info=True)

            return {
                "normalized_symptoms": [],
                "symptom_categories": {},
                "normalization_success": False,
                "error": str(e),
                "agent": self.name,
                "timestamp": datetime.datetime.now().isoformat()
            }