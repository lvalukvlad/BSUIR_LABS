from .base_agent import BaseAgent
import json
import logging
from typing import Dict, Any, List, Union, Optional

logger = logging.getLogger(__name__)

try:
    from utils.ollama_client import OllamaClient

    OLLAMA_CLIENT_AVAILABLE = True
except ImportError:
    OLLAMA_CLIENT_AVAILABLE = False
    OllamaClient = None


class LocalizationExpert(BaseAgent):
    def __init__(self, llm_client=None):
        super().__init__(name="LocalizationExpert", llm_client=llm_client)

        if llm_client is None and OLLAMA_CLIENT_AVAILABLE:
            try:
                from config.settings import get_settings
                settings = get_settings()

                self.llm = OllamaClient(
                    base_url=settings.OLLAMA_BASE_URL,
                    model=settings.OLLAMA_MODEL,
                    temperature=settings.OLLAMA_TEMPERATURE,
                    timeout=settings.OLLAMA_TIMEOUT
                )
                self.use_llm = self.llm.is_available()
            except Exception as e:
                logger.error(f"Failed to initialize Ollama: {e}")
                self.use_llm = False
        else:
            self.llm = llm_client
            self.use_llm = llm_client is not None

    async def process(self, state: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
        symptoms_text = self._extract_symptoms_text(state)

        if not symptoms_text.strip():
            return {
                "localizations": [],
                "suggested_diagnosis": None,
                "localization_success": False,
                "error": "No symptoms provided"
            }

        if self.use_llm and self.llm and symptoms_text:
            try:
                localizations_result = await self._get_localization_with_llm(symptoms_text)
                return localizations_result
            except Exception as e:
                logger.error(f"LLM localization failed: {e}")

        localizations = self._extract_localizations_from_keywords(symptoms_text)

        result = {
            "localizations": localizations,
            "suggested_diagnosis": None,
            "localization_success": True,
            "method": "keyword_based",
            "localizations_count": len(localizations)
        }

        return result

    def _extract_symptoms_text(self, state: Any) -> str:
        symptoms = []

        if hasattr(state, 'symptom_texts'):
            symptoms = getattr(state, 'symptom_texts', [])
        elif hasattr(state, 'get_symptoms_for_processing'):
            symptoms = state.get_symptoms_for_processing()
        elif hasattr(state, 'get_normalized_symptoms'):
            symptoms = state.get_normalized_symptoms()
        else:
            symptoms_data = self._safe_get(state, 'symptoms', [])
            if symptoms_data and isinstance(symptoms_data, list):
                for item in symptoms_data:
                    if isinstance(item, dict):
                        symptoms.append(item.get('text', item.get('normalized', str(item))))
                    else:
                        symptoms.append(str(item))
            elif isinstance(state, str):
                symptoms = [state]

        return " ".join([s.strip() for s in symptoms if s and str(s).strip()])

    async def _get_localization_with_llm(self, symptoms_text: str) -> Dict[str, Any]:
        try:
            prompt = f"""Определи локализацию симптомов:

Симптомы: {symptoms_text}

Ответь в формате JSON:
{{
    "localizations": ["локализация1", "локализация2"],
    "suggested_diagnosis": "предварительный диагноз или null"
}}"""

            response_text = await self.generate_with_llm(
                prompt=prompt,
                system_prompt="Будь точным в определении локализации симптомов. Отвечай ТОЛЬКО в формате JSON.",
                max_tokens=300
            )

            if not response_text:
                logger.warning("Empty response from LLM")
                return self._fallback_localization(symptoms_text)

            result = self._parse_llm_response(response_text)

            return {
                "localizations": result.get("localizations", []),
                "suggested_diagnosis": result.get("suggested_diagnosis"),
                "localization_success": True,
                "method": "llm_based",
                "localizations_count": len(result.get("localizations", []))
            }

        except Exception as e:
            logger.error(f"LLM localization error: {e}")
            return self._fallback_localization(symptoms_text)

    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        try:
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()

            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')

            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx + 1]
                result = json.loads(json_str)

                localizations = result.get("localizations", [])
                if isinstance(localizations, str):
                    localizations = [localizations]
                elif not isinstance(localizations, list):
                    localizations = []

                return {
                    "localizations": [str(loc) for loc in localizations if loc],
                    "suggested_diagnosis": result.get("suggested_diagnosis")
                }

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"Failed to parse LLM response: {e}")

        return {"localizations": [], "suggested_diagnosis": None}

    def _fallback_localization(self, symptoms_text: str) -> Dict[str, Any]:
        localizations = self._extract_localizations_from_keywords(symptoms_text)

        return {
            "localizations": localizations,
            "suggested_diagnosis": None,
            "localization_success": True,
            "method": "keyword_fallback",
            "localizations_count": len(localizations)
        }

    def _extract_localizations_from_keywords(self, symptoms_text: str) -> List[str]:
        localizations = []
        symptoms_lower = symptoms_text.lower()

        localization_map = {
            "голов": "голова",
            "виск": "висок",
            "затыл": "затылок",
            "лоб": "лоб",
            "спин": "спина",
            "живот": "живот",
            "груд": "грудь",
            "горл": "горло",
            "рука": "рука",
            "кисть": "кисть",
            "нога": "нога",
            "ступн": "ступня",
            "сердц": "сердце",
            "сердечн": "сердце",
            "легк": "легкие",
            "дыхан": "дыхательные пути",
            "сустав": "суставы",
            "мышц": "мышцы",
            "живот": "живот",
            "поясни": "поясница",
            "шей": "шея",
            "горл": "горло",
            "нос": "нос",
            "ух": "ухо",
            "горл": "горло",
            "зуб": "зубы",
            "челюст": "челюсть",
            "плеч": "плечо",
            "колен": "колено",
            "лодыжк": "лодыжка",
            "запяст": "запястье"
        }

        for keyword, localization in localization_map.items():
            if keyword in symptoms_lower and localization not in localizations:
                localizations.append(localization)

        return localizations