from .base_agent import BaseAgent
import logging
from typing import Dict, Any, List, Union

logger = logging.getLogger(__name__)


class ContraindicationsCollector(BaseAgent):
    """Агент сбора информации о противопоказаниях"""

    def __init__(self, llm_client=None):
        super().__init__(name="ContraindicationsCollector", llm_client=llm_client)

    async def process(self, state: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
        """Определяет, какие вопросы задать о противопоказаниях"""

        # Проверяем, есть ли уже информация
        contraindications_data = self._extract_contraindications(state)

        if contraindications_data and self._has_sufficient_contraindications(contraindications_data):
            return {
                "needs_contraindications": False,
                "contraindications_questions": [],
                "contraindications_collected": True
            }

        # Определяем, какие вопросы задать
        questions = self._generate_contraindications_questions(contraindications_data)

        return {
            "needs_contraindications": True,
            "contraindications_questions": questions,
            "questions_count": len(questions)
        }

    def _extract_contraindications(self, state: Any) -> Dict[str, Any]:
        """Извлекает информацию о противопоказаниях"""

        contraindications = {}

        # Пробуем разные источники
        if hasattr(state, 'contraindications'):
            contraindications_obj = getattr(state, 'contraindications')
            if hasattr(contraindications_obj, 'to_dict'):
                contraindications = contraindications_obj.to_dict()
            elif isinstance(contraindications_obj, dict):
                contraindications = contraindications_obj

        # Или из user_profile
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

        return contraindications

    def _has_sufficient_contraindications(self, contraindications: Dict) -> bool:
        """Проверяет, достаточно ли информации о противопоказаниях"""

        # Минимальные требования
        if contraindications.get('allergies') is not None:
            return True

        if contraindications.get('chronic_conditions') is not None:
            return True

        # Если есть хотя бы подтверждение "нет противопоказаний"
        if 'no_contraindications' in contraindications:
            return True

        return False

    def _generate_contraindications_questions(self, existing_data: Dict) -> List[str]:
        """Генерирует вопросы о противопоказаниях"""

        questions = []

        # Определяем, что уже известно
        known_allergies = bool(existing_data.get('allergies'))
        known_conditions = bool(existing_data.get('chronic_conditions'))
        known_medications = bool(existing_data.get('current_medications'))
        known_pregnancy = existing_data.get('pregnancy') is not None

        # Основные вопросы
        if not known_allergies:
            questions.append("• Есть ли у вас аллергии на лекарства или продукты? (если нет, напишите 'нет')")

        if not known_conditions:
            questions.append("• Есть ли хронические заболевания? (печень, почки, сердце, диабет и т.д.)")

        if not known_medications:
            questions.append("• Принимаете ли вы сейчас какие-либо лекарства постоянно?")

        if not known_pregnancy:
            questions.append("• Вы беременны или кормите грудью? (да/нет)")

        # Ограничиваем 3 вопросами за раз
        return questions[:3]

    async def parse_user_response(self, user_response: str) -> Dict[str, Any]:
        """Парсит ответ пользователя о противопоказаниях"""

        prompt = f"""Проанализируй ответ пользователя о противопоказаниях:

        Ответ: {user_response}

        Извлеки информацию:
        1. Аллергии (список или "нет")
        2. Хронические заболевания
        3. Текущие лекарства
        4. Беременность/лактация
        5. Другие ограничения

        Ответь в формате JSON:
        {{
            "allergies": ["аллергия1"] или "нет",
            "chronic_conditions": ["заболевание1"] или "нет", 
            "current_medications": ["лекарство1"] или "нет",
            "pregnancy": true/false/null,
            "breastfeeding": true/false/null,
            "kidney_problems": true/false/null,
            "liver_problems": true/false/null,
            "other_restrictions": ["ограничение1"]
        }}"""

        response = await self.generate_with_llm(
            prompt=prompt,
            system_prompt="Извлекай информацию точно. Если пользователь пишет 'нет' - ставь соответствующий флаг.",
            max_tokens=500
        )

        if not response:
            return self._simple_parse(user_response)

        try:
            import json
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return self._simple_parse(user_response)

    def _simple_parse(self, user_response: str) -> Dict[str, Any]:
        """Простой парсинг ответа"""

        response_lower = user_response.lower()

        result = {
            "allergies": [],
            "chronic_conditions": [],
            "current_medications": [],
            "pregnancy": None,
            "breastfeeding": None,
            "kidney_problems": None,
            "liver_problems": None,
            "other_restrictions": []
        }

        # Простая логика
        if 'нет аллерги' in response_lower or 'аллергий нет' in response_lower:
            result["allergies"] = "нет"

        if 'беременн' in response_lower:
            result["pregnancy"] = True

        if 'кормлю груд' in response_lower or 'лактаци' in response_lower:
            result["breastfeeding"] = True

        if 'печень' in response_lower or 'гепатит' in response_lower:
            result["liver_problems"] = True

        if 'почк' in response_lower or 'нефрит' in response_lower:
            result["kidney_problems"] = True

        return result