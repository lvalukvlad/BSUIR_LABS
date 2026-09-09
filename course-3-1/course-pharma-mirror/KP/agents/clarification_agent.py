from .base_agent import BaseAgent
from typing import Dict, Any, List, Union
import logging

logger = logging.getLogger(__name__)

from .base_agent import BaseAgent
from typing import Dict, Any, List, Union
import logging

logger = logging.getLogger(__name__)


class ClarificationAgent(BaseAgent):
    def __init__(self, llm_client=None):
        super().__init__(name="ClarificationAgent", llm_client=llm_client)
        self.previous_questions = {}
        self.conversation_clarification_history = {}

    async def process(self, state: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
        conversation_id = self._extract_conversation_id(state)

        clarification_attempts = self._extract_clarification_attempts(state)

        max_attempts = self._extract_max_attempts(state)
        if clarification_attempts >= max_attempts:
            return {
                "clarification_questions": [],
                "needs_clarification": False,
                "max_attempts_reached": True
            }

        symptoms_data = self._extract_symptoms_data(state)
        diagnosis_data = self._extract_diagnosis_data(state)

        diagnosis_confidence = diagnosis_data.get('confidence', 0) if diagnosis_data else 0

        if diagnosis_confidence < 0.7 and clarification_attempts < max_attempts:
            missing_info = await self._analyze_missing_info_with_llm(
                symptoms_data,
                diagnosis_data,
                conversation_id
            )

            if missing_info:
                questions = await self._generate_smart_clarification_questions(
                    missing_info,
                    symptoms_data,
                    conversation_id
                )

                if questions:
                    if conversation_id not in self.conversation_clarification_history:
                        self.conversation_clarification_history[conversation_id] = []

                    self.conversation_clarification_history[conversation_id].extend([
                        {"question": q, "attempt": clarification_attempts + 1}
                        for q in questions
                    ])

                    return {
                        "clarification_questions": questions,
                        "needs_clarification": True,
                        "missing_info_types": missing_info,
                        "questions_count": len(questions),
                        "attempt_number": clarification_attempts + 1
                    }

        return {
            "clarification_questions": [],
            "needs_clarification": False,
            "all_info_available": True
        }

    async def _analyze_missing_info_with_llm(self, symptoms: Any, diagnosis: Dict, conversation_id: str) -> List[str]:
        symptoms_text = self._extract_symptoms_text(symptoms)

        prompt = f"""Проанализируй, какая информация отсутствует для точного диагноза:

        Симптомы: {symptoms_text}
        Диагноз: {diagnosis.get('diagnosis', 'Не установен')}
        Уверенность: {diagnosis.get('confidence', 0)}

        История уже заданных вопросов в этой беседе:
        {self._get_asked_questions_text(conversation_id)}

        Определи 1-2 самых важных недостающих аспекта из:
        - локализация (где именно болит)
        - интенсивность (сила боли по шкале 1-10)
        - длительность (сколько времени продолжается)
        - характер (острый, тупой, пульсирующий)
        - сопутствующие симптомы (температура, тошнота и т.д.)
        - провоцирующие факторы (что усиливает)
        - облегчающие факторы (что помогает)
        - начало (внезапное или постепенное)

        Ответь в формате: ["аспект1", "аспект2"]"""

        response = await self.generate_with_llm(
            prompt=prompt,
            system_prompt="Будь точен. Выбирай наиболее важные для диагноза аспекты.",
            max_tokens=300
        )

        if not response:
            return self._analyze_missing_info_fallback(symptoms_text, conversation_id)

        try:
            import re
            import json
            list_match = re.search(r'\[.*\]', response)
            if list_match:
                missing_info = json.loads(list_match.group())
                return missing_info[:2]
        except:
            pass

        return self._analyze_missing_info_fallback(symptoms_text, conversation_id)

    def _get_asked_questions_text(self, conversation_id: str) -> str:
        if conversation_id not in self.conversation_clarification_history:
            return "Еще не задано вопросов"

        questions = [q["question"] for q in self.conversation_clarification_history[conversation_id]]
        return "\n".join([f"- {q}" for q in questions[-5:]])

    async def _generate_smart_clarification_questions(self,
                                                      missing_info: List[str],
                                                      symptoms: Any,
                                                      conversation_id: str) -> List[str]:
        symptoms_text = self._extract_symptoms_text(symptoms)
        asked_questions = self._get_asked_questions(conversation_id)

        prompt = f"""Сгенерируй 1-2 конкретных вопроса для уточнения диагноза:

        Симптомы: {symptoms_text}

        Что нужно уточнить: {', '.join(missing_info)}

        Уже заданные вопросы (не повторяй их):
        {asked_questions}

        Сгенерируй максимально конкретные вопросы, например:
        - "Какая именно температура? Измеряли?"
        - "Боль острая или тупая?"
        - "Есть ли гной в горле?"

        Ответь в формате:
        1. Вопрос первый?
        2. Вопрос второй?"""

        response = await self.generate_with_llm(
            prompt=prompt,
            system_prompt="Генерируй конкретные, медицински релевантные вопросы. Будь кратким.",
            max_tokens=400
        )

        if not response:
            return self._generate_clarification_questions_fallback(missing_info, conversation_id)

        questions = []
        lines = response.strip().split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '- ', '• ')):
                question = line[2:].strip() if '. ' in line[:3] else line[2:].strip()
                if question and len(question) > 5:
                    questions.append(question)

        filtered_questions = []
        for q in questions:
            if not self._is_question_similar(q, asked_questions):
                filtered_questions.append(q)

        return filtered_questions[:2]

    def _get_asked_questions(self, conversation_id: str) -> List[str]:
        if conversation_id not in self.conversation_clarification_history:
            return []
        return [q["question"] for q in self.conversation_clarification_history[conversation_id]]

    def _is_question_similar(self, new_question: str, asked_questions: List[str]) -> bool:
        new_q_lower = new_question.lower()

        for asked_q in asked_questions:
            asked_lower = asked_q.lower()
            if (len(set(new_q_lower.split()) & set(asked_lower.split())) > 2 or
                    any(word in new_q_lower for word in asked_lower.split()[:3])):
                return True

        return False

    def _extract_diagnosis_data(self, state: Any) -> Dict:
        if hasattr(state, 'preliminary_diagnosis'):
            prelim = getattr(state, 'preliminary_diagnosis')
            if isinstance(prelim, dict):
                return prelim
        return {}

    def _extract_max_attempts(self, state: Any) -> int:
        if hasattr(state, 'max_clarification_attempts'):
            return getattr(state, 'max_clarification_attempts')
        return 2

    def _extract_symptoms_data(self, state: Any) -> Any:
        if hasattr(state, 'get_symptoms_for_processing'):
            return state.get_symptoms_for_processing()
        elif hasattr(state, 'symptoms'):
            return getattr(state, 'symptoms', [])
        elif hasattr(state, 'symptom_texts'):
            return getattr(state, 'symptom_texts', [])
        else:
            return self._safe_get(state, 'symptoms', [])

    def _extract_symptoms_text(self, symptoms_data: Any) -> str:
        if not symptoms_data:
            return ""

        symptoms_text_parts = []

        if isinstance(symptoms_data, list):
            for symptom in symptoms_data:
                if isinstance(symptom, str):
                    symptoms_text_parts.append(symptom)
                elif isinstance(symptom, dict):
                    text = symptom.get('text', symptom.get('normalized', symptom.get('description', '')))
                    if text:
                        symptoms_text_parts.append(text)
                elif hasattr(symptom, 'description'):
                    symptoms_text_parts.append(symptom.description)
                elif hasattr(symptom, 'text'):
                    symptoms_text_parts.append(symptom.text)
                else:
                    symptoms_text_parts.append(str(symptom))
        elif isinstance(symptoms_data, str):
            symptoms_text_parts.append(symptoms_data)
        else:
            symptoms_text_parts.append(str(symptoms_data))

        return " ".join(symptoms_text_parts)

    def _extract_conversation_id(self, state: Any) -> str:
        conversation_id = self._safe_get(state, 'conversation_id')
        if not conversation_id:
            context = self._safe_get(state, 'context')
            if context:
                if isinstance(context, dict):
                    conversation_id = context.get('conversation_id', '')
                elif hasattr(context, 'conversation_id'):
                    conversation_id = getattr(context, 'conversation_id', '')

        return str(conversation_id) if conversation_id else ""

    def _extract_clarification_attempts(self, state: Any) -> int:
        attempts = self._safe_get(state, 'clarification_attempts', 0)
        try:
            return int(attempts)
        except (ValueError, TypeError):
            return 0

    def _analyze_missing_info(self, symptoms_text: str, conversation_id: str = "") -> List[str]:
        if not symptoms_text or len(symptoms_text.strip()) < 5:
            return ["location", "intensity", "duration", "accompanying"]

        symptoms_lower = symptoms_text.lower()
        missing = []

        location_keywords = ['голов', 'виск', 'затыл', 'лоб', 'спин', 'живот', 'груд', 'горл', 'право', 'лево']
        location_found = any(keyword in symptoms_lower for keyword in location_keywords)

        if not location_found and not self._was_question_asked("location", conversation_id):
            missing.append("location")

        intensity_keywords = ['сильн', 'слаб', 'умерен', 'остр', 'туп', 'пульсир', 'ноющ', 'интенсивность', 'шкал',
                              'балл', 'оценк']
        intensity_found = any(keyword in symptoms_lower for keyword in intensity_keywords)

        if not intensity_found and not self._was_question_asked("intensity", conversation_id):
            missing.append("intensity")

        time_keywords = ['час', 'день', 'недел', 'давно', 'утр', 'вечер', 'минут', 'секунд', 'дней', 'недель', 'месяц']
        time_found = any(keyword in symptoms_lower for keyword in time_keywords)

        if not time_found and not self._was_question_asked("duration", conversation_id):
            missing.append("duration")

        accompanying_keywords = ['температур', 'тошнот', 'рвот', 'головокруж', 'слабост', 'озноб', 'потлив', 'устал',
                                 'утомл']
        accompanying_found = any(keyword in symptoms_lower for keyword in accompanying_keywords)

        if not accompanying_found and not self._was_question_asked("accompanying", conversation_id):
            missing.append("accompanying")

        return missing

    def _was_question_asked(self, info_type: str, conversation_id: str) -> bool:
        if conversation_id not in self.previous_questions:
            return False

        asked_questions = self.previous_questions[conversation_id]
        question_patterns = {
            "location": ["где", "локализ", "место", "болит"],
            "intensity": ["интенсив", "сильн", "слаб", "шкал", "балл"],
            "duration": ["давно", "время", "начал", "появил"],
            "accompanying": ["другие", "сопутств", "симптомы", "есть ли"]
        }

        if info_type not in question_patterns:
            return False

        for question in asked_questions:
            question_lower = question.lower()
            for pattern in question_patterns[info_type]:
                if pattern in question_lower:
                    return True

        return False

    def _generate_clarification_questions(self, missing_info: List[str], attempt: int = 0, conversation_id: str = "") -> \
    List[str]:
        if attempt >= 1:
            important_info = ["location", "intensity"]
            missing_info = [info for info in missing_info if info in important_info]

        asked_questions = self.previous_questions.get(conversation_id, [])
        asked_texts = [q.lower() for q in asked_questions]

        questions = []
        question_templates = {
            "location": "• Где именно болит? (лоб, виски, затылок, спина, живот и т.д.)",
            "intensity": "• Какова интенсивность боли? (сильная, слабая, умеренная, по шкале 1-10)",
            "duration": "• Как давно появились симптомы? (часы, дни, недели)",
            "accompanying": "• Есть ли другие симптомы? (температура, тошнота, слабость, головокружение)"
        }

        for info_type in missing_info[:2]:
            if info_type in question_templates:
                question = question_templates[info_type]
                if not self._is_similar_question_asked(question, asked_texts):
                    questions.append(question)

        return questions

    def _is_similar_question_asked(self, question: str, asked_questions: List[str]) -> bool:
        question_lower = question.lower()

        for asked in asked_questions:
            words_q = set(question_lower.split())
            words_a = set(asked.split())
            common_words = words_q.intersection(words_a)

            if len(common_words) >= 2:
                return True

        return False

    def clear_conversation_cache(self, conversation_id: str):
        if conversation_id in self.previous_questions:
            del self.previous_questions[conversation_id]


    def _generate_clarification_questions_fallback(self, missing_info: List[str], conversation_id: str) -> List[str]:
        questions = []

        question_map = {
            "локализация": "• Где именно болит? (лоб, виски, затылок, горло, живот)",
            "интенсивность": "• Какова интенсивность боли? (сильная, слабая, умеренная)",
            "длительность": "• Как давно появились симптомы?",
            "характер": "• Какой характер боли? (острая, тупая, пульсирующая)",
            "сопутствующие": "• Есть ли другие симптомы? (температура, слабость)"
        }

        for info in missing_info[:2]:
            if info in question_map:
                questions.append(question_map[info])

        return questions