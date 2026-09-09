"""
Оркестратор агентов для медицинской системы
"""
from typing import Dict, Any, List, Optional
import asyncio
import logging
from datetime import datetime
import uuid
import traceback
from core.conversation_context import ConversationContext, ConversationStage
from core.workflow_engine import WorkflowEngine, WorkflowNode, ParallelWorkflowNode
from core.workflow_definitions import get_all_workflow_definitions

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Оркестратор для управления агентами и workflow"""

    # В AgentOrchestrator добавляем метод:
    async def _handle_localization_analysis(self, context: ConversationContext) -> Dict[str, Any]:
        """Анализ локализации симптомов"""

        logger.info(f"Starting localization analysis for conversation: {context.conversation_id}")

        if "localization_expert" not in self.agents:
            # Пропускаем если нет агента
            context.current_stage = ConversationStage.DIAGNOSIS
            return {
                "response": "Перехожу к диагностике...",
                "conversation_id": context.conversation_id,
                "stage": context.current_stage.value,
                "needs_input": False
            }

        try:
            # Запускаем LocalizationExpert
            localization_result = await self.agents["localization_expert"].process(context)

            if localization_result and localization_result.get("localization_success", False):
                # Сохраняем результаты
                localizations = localization_result.get("localizations", [])

                # Создаем LocalizationInfo
                from core.conversation_context import LocalizationInfo
                localization_info = LocalizationInfo(
                    primary_location=localizations[0] if localizations else None,
                    specific_locations=localizations,
                    laterality=self._determine_laterality(localizations),
                    anatomical_system=self._determine_anatomical_system(localizations)
                )

                context.localization_info = localization_info

                # Сохраняем анализ
                context.localization_analysis = {
                    "localizations": localizations,
                    "suggested_diagnosis": localization_result.get("suggested_diagnosis"),
                    "method": localization_result.get("method", "unknown"),
                    "timestamp": datetime.now().isoformat()
                }

                # Формируем сообщение о результатах
                if localizations:
                    response = f"📍 **Анализ локализации завершен:**\n\n"
                    response += f"**Основные локализации:** {', '.join(localizations[:3])}\n"

                    if localization_result.get("suggested_diagnosis"):
                        response += f"**Подсказка по диагнозу:** {localization_result['suggested_diagnosis']}\n"

                    response += "\nПерехожу к диагностике..."
                else:
                    response = "📍 Локализация симптомов не определена. Перехожу к диагностике..."

            else:
                response = "📍 Анализ локализации не удался. Перехожу к диагностике..."

            # Переходим к следующему этапу
            context.current_stage = ConversationStage.DIAGNOSIS
            context.add_message("assistant", response)

            # Запускаем диагностику асинхронно
            asyncio.create_task(self._handle_diagnosis(context))

            return {
                "response": response,
                "conversation_id": context.conversation_id,
                "stage": context.current_stage.value,
                "needs_input": False,
                "localizations": localization_result.get("localizations", []) if localization_result else []
            }

        except Exception as e:
            logger.error(f"Localization analysis failed: {e}", exc_info=True)

            # В случае ошибки просто переходим к диагностике
            context.current_stage = ConversationStage.DIAGNOSIS
            response = "Перехожу к диагностике..."
            context.add_message("assistant", response)

            asyncio.create_task(self._handle_diagnosis(context))

            return {
                "response": response,
                "conversation_id": context.conversation_id,
                "stage": context.current_stage.value,
                "needs_input": False
            }

    def _determine_laterality(self, localizations: List[str]) -> Optional[str]:
        """Определяет латеральность (одностороннее/двустороннее)"""
        if not localizations:
            return None

        location_text = ' '.join(localizations).lower()

        if any(word in location_text for word in ['право', 'правый', 'правой', 'right']):
            if any(word in location_text for word in ['лево', 'левый', 'левой', 'left']):
                return "bilateral"
            return "right"
        elif any(word in location_text for word in ['лево', 'левый', 'левой', 'left']):
            return "left"

        return "unknown"

    def _determine_anatomical_system(self, localizations: List[str]) -> Optional[str]:
        """Определяет анатомическую систему"""
        system_map = {
            'голов': 'neurological',
            'спин': 'musculoskeletal',
            'живот': 'gastrointestinal',
            'груд': 'cardiovascular',
            'горл': 'respiratory',
            'сердц': 'cardiovascular',
            'легк': 'respiratory',
            'почк': 'urinary',
            'печен': 'hepatic',
            'сустав': 'musculoskeletal',
            'мышц': 'musculoskeletal'
        }

        for loc in localizations:
            loc_lower = loc.lower()
            for keyword, system in system_map.items():
                if keyword in loc_lower:
                    return system

        return "general"

    def __init__(self, agents: Dict[str, Any]):
        self.agents = agents
        self.workflow_engine = WorkflowEngine()
        self.conversations: Dict[str, ConversationContext] = {}

        # Регистрируем workflow
        self._register_workflows()

        logger.info(f"AgentOrchestrator initialized with {len(agents)} agents")
        logger.info(f"Available agents: {list(agents.keys())}")

    def _register_workflows(self):
        """Регистрирует все workflow"""
        try:
            workflow_defs = get_all_workflow_definitions(self.agents)

            for name, workflow in workflow_defs.items():
                self.workflow_engine.register_workflow(name, workflow)

            logger.info(f"Registered {len(workflow_defs)} workflows: {list(workflow_defs.keys())}")
        except Exception as e:
            logger.error(f"Failed to register workflows: {e}")
            # Создаем простые workflow как fallback
            self._register_fallback_workflows()

    def _register_fallback_workflows(self):
        """Регистрирует fallback workflow"""
        # Простой workflow для диагностики
        diagnosis_workflow = [
            WorkflowNode(
                name="symptom_normalization",
                agent=self.agents.get("symptom_normalizer"),
                description="Нормализация симптомов"
            ),
            WorkflowNode(
                name="diagnosis",
                agent=self.agents.get("diagnostician"),
                description="Постановка диагноза"
            ),
            WorkflowNode(
                name="severity_assessment",
                agent=self.agents.get("severity_evaluator"),
                description="Оценка серьезности"
            )
        ]

        self.workflow_engine.register_workflow("diagnosis", diagnosis_workflow)
        logger.info("Registered fallback diagnosis workflow")

    def create_conversation(self,
                            user_id: Optional[str] = None,
                            session_id: Optional[str] = None,
                            conversation_id: Optional[str] = None) -> ConversationContext:
        """Создает новую беседу с возможностью указать ID"""

        # Если передан conversation_id, используем его
        if conversation_id:
            # Проверяем не существует ли уже беседа с таким ID
            if conversation_id in self.conversations:
                logger.warning(f"Conversation {conversation_id} already exists, returning existing")
                return self.conversations[conversation_id]

            # Создаем контекст с указанным ID
            context = ConversationContext(
                conversation_id=conversation_id,
                user_id=user_id,
                session_id=session_id
            )
        else:
            # Или создаем с автоматическим ID
            context = ConversationContext(user_id=user_id, session_id=session_id)

        key = context.conversation_id
        self.conversations[key] = context

        logger.info(f"Created conversation: {key}")
        return context

    def get_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """Получает беседу по ID - ДОБАВЬТЕ ЛОГИРОВАНИЕ"""
        logger.debug(f"Looking for conversation: {conversation_id}")
        logger.debug(f"Available conversations: {list(self.conversations.keys())}")

        result = self.conversations.get(conversation_id)
        if result:
            logger.debug(f"Found conversation: {conversation_id}")
        else:
            logger.debug(f"Conversation not found: {conversation_id}")

        return result

    def update_conversation(self, conversation_id: str, context: ConversationContext):
        """Обновляет беседу"""
        self.conversations[conversation_id] = context

    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """Получает историю сообщений беседы"""
        conversation = self.get_conversation(conversation_id)
        if conversation:
            return conversation.messages
        return []

    # В методе process_conversation добавить больше логов:
    async def process_conversation(self, conversation_id: str, user_input: str) -> Dict[str, Any]:
        """Обработка разговора с улучшенным логированием"""

        context = self.get_conversation(conversation_id)
        if not context:
            context = self.create_conversation(conversation_id=conversation_id)
            logger.info(f"📝 Created NEW conversation: {conversation_id}")

        context.add_message("user", user_input)

        logger.info(f"🔄 Processing conversation {conversation_id}")
        logger.info(f"   Stage: {context.current_stage}")
        logger.info(f"   User input: '{user_input[:100]}...'")
        logger.info(f"   Symptom texts: {len(context.symptom_texts)} items")
        logger.info(f"   Clarification attempts: {context.clarification_attempts_count}")

        # Логируем все возможные состояния
        logger.debug(f"   Has symptoms: {context.symptoms_collected}")
        logger.debug(f"   Has contraindications: {context.contraindications_collected}")
        logger.debug(f"   Needs clarification: {context.needs_clarification}")

        # Обрабатываем в зависимости от стадии
        if context.current_stage == ConversationStage.GREETING:
            logger.info("   → Handling GREETING")
            return await self._handle_greeting(context)

        elif context.current_stage == ConversationStage.CONTRAINDICATIONS_COLLECTION:
            logger.info("   → Handling CONTRAINDICATIONS_COLLECTION")
            return await self._handle_contraindications(context, user_input)

        elif context.current_stage == ConversationStage.SYMPTOM_COLLECTION:
            logger.info("   → Handling SYMPTOM_COLLECTION")
            return await self._handle_symptom_collection(context, user_input)

        elif context.current_stage == ConversationStage.LOCALIZATION_ANALYSIS:
            logger.info("   → Handling LOCALIZATION_ANALYSIS")
            return await self._handle_localization_analysis(context)

        elif context.current_stage == ConversationStage.CLARIFICATION:
            logger.info("   → Handling CLARIFICATION")
            logger.info(f"   Clarification questions: {context.clarification_questions}")
            return await self._handle_clarification(context, user_input)

        elif context.current_stage == ConversationStage.DIAGNOSIS:
            logger.info("   → Handling DIAGNOSIS")
            return await self._handle_diagnosis(context)

        elif context.current_stage == ConversationStage.TREATMENT:
            logger.info("   → Handling TREATMENT")
            return await self._handle_treatment(context)

        else:
            logger.warning(f"   → Unknown stage: {context.current_stage}, falling back")
            return await self._handle_unknown(context)

    def debug_conversation_state(self, conversation_id: str):
        """Выводит отладочную информацию о беседе"""

        context = self.get_conversation(conversation_id)
        if not context:
            print(f"❌ Conversation {conversation_id} not found")
            return

        print(f"\n🔍 DEBUG: Conversation {conversation_id}")
        print(f"   Stage: {context.current_stage}")
        print(f"   Symptoms: {len(context.symptom_texts)}")
        for i, symptom in enumerate(context.symptom_texts):
            print(f"     {i + 1}. {symptom[:50]}...")

        print(f"   Clarification attempts: {context.clarification_attempts_count}")
        print(f"   Needs clarification: {context.needs_clarification}")
        print(f"   Has diagnosis: {context.primary_diagnosis is not None}")

        if context.primary_diagnosis:
            print(f"   Diagnosis: {context.primary_diagnosis.name}")
            print(f"   Confidence: {context.primary_diagnosis.confidence}")

        # Проверяем наличие normalized_symptoms
        if hasattr(context, 'normalized_symptoms'):
            print(f"   Normalized symptoms: {len(context.normalized_symptoms)}")

        print(f"   Messages in history: {len(context.messages)}")

    async def _handle_greeting(self, context: ConversationContext) -> Dict[str, Any]:
        """Начало разговора"""

        greeting = """👋 **Здравствуйте! Я медицинский помощник.**

    Для безопасных рекомендаций мне нужно узнать о возможных противопоказаниях.

    Пожалуйста, ответьте на несколько вопросов:

    1. Есть ли у вас аллергии на лекарства?
    2. Есть ли хронические заболевания?
    3. Принимаете ли вы сейчас какие-либо лекарства?
    4. Беременны или кормите грудью?

    Можете ответить одним сообщением, например: "Аллергии нет, хронических заболеваний нет, лекарств не принимаю, не беременна"."""

        context.add_message("assistant", greeting)
        context.current_stage = ConversationStage.CONTRAINDICATIONS_COLLECTION

        return {
            "response": greeting,
            "conversation_id": context.conversation_id,
            "stage": context.current_stage.value,
            "needs_input": True
        }

    async def _handle_contraindications(self, context: ConversationContext, user_input: str) -> Dict[str, Any]:
        """Обработка противопоказаний"""

        if "contraindications_collector" not in self.agents:
            # Пропускаем сбор противопоказаний если нет агента
            context.current_stage = ConversationStage.SYMPTOM_COLLECTION
            response = "✅ Спасибо. Теперь опишите ваши симптомы."
            context.add_message("assistant", response)

            return {
                "response": response,
                "conversation_id": context.conversation_id,
                "stage": context.current_stage.value,
                "needs_input": True
            }

        # Парсим ответ о противопоказаниях
        collector = self.agents["contraindications_collector"]
        parsed_contraindications = await collector.parse_user_response(user_input)

        # Обновляем контекст
        context.update_contraindications(**parsed_contraindications)

        # Проверяем, достаточно ли информации
        check_result = await collector.process(context)

        if check_result.get("needs_contraindications", False):
            # Нужны еще уточнения
            questions = check_result.get("contraindications_questions", [])
            response = "Пожалуйста, уточните:\n" + "\n".join(questions)

            context.add_message("assistant", response)

            return {
                "response": response,
                "conversation_id": context.conversation_id,
                "stage": context.current_stage.value,
                "needs_input": True,
                "contraindications_questions": questions
            }
        else:
            # Достаточно информации, переходим к симптомам
            context.current_stage = ConversationStage.SYMPTOM_COLLECTION

            response = """✅ Спасибо за информацию о противопоказаниях.

    Теперь опишите, что вас беспокоит:
    • Какие симптомы?
    • Как долго?
    • Что усиливает или облегчает?"""

            context.add_message("assistant", response)

            return {
                "response": response,
                "conversation_id": context.conversation_id,
                "stage": context.current_stage.value,
                "needs_input": True
            }

    async def _handle_symptom_collection(self, context: ConversationContext, user_input: str) -> Dict[str, Any]:
        """Сбор симптомов - ИСПРАВЛЕННЫЙ"""

        logger.info(f"📝 Adding symptom: '{user_input[:50]}...'")

        # Добавляем симптом
        context.add_symptom(user_input)
        context.symptoms_collected = True

        logger.info(f"   ✅ Symptom added. Total symptoms: {len(context.symptom_texts)}")
        logger.info(f"   Symptom texts: {context.symptom_texts}")

        try:
            # Нормализуем симптомы
            if "symptom_normalizer" in self.agents:
                logger.info("   🔄 Normalizing symptoms...")
                normalization_result = await self.agents["symptom_normalizer"].process({
                    "symptoms": context.symptom_texts,
                    "conversation_id": context.conversation_id
                })

                if normalization_result:
                    context.update(**normalization_result)
                    logger.info(f"   ✅ Normalized {len(normalization_result.get('normalized_symptoms', []))} symptoms")
        except Exception as e:
            logger.error(f"   ❌ Symptom normalization failed: {e}")

        # Проверяем, достаточно ли симптомов для диагноза
        if len(context.symptom_texts) >= 1:  # Минимум 1 симптом
            context.current_stage = ConversationStage.DIAGNOSIS

            response = "✅ Спасибо. Анализирую симптомы..."
            context.add_message("assistant", response)

            # Запускаем диагностику асинхронно
            asyncio.create_task(self._handle_diagnosis(context))

            return {
                "response": response,
                "conversation_id": context.conversation_id,
                "stage": context.current_stage.value,
                "needs_input": False
            }
        else:
            # Просим больше симптомов
            response = "Пожалуйста, опишите симптомы подробнее. Что именно беспокоит?"
            context.add_message("assistant", response)

            return {
                "response": response,
                "conversation_id": context.conversation_id,
                "stage": context.current_stage.value,
                "needs_input": True
            }

    # В agent_orchestrator.py добавить между симптомами и диагнозом:
    async def _handle_localization_analysis(self, context: ConversationContext):
        """Анализ локализации симптомов"""
        if "localization_expert" in self.agents:
            localization_result = await self.agents["localization_expert"].process(context)
            # Сохранить результат в контекст

    async def _handle_diagnosis(self, context: ConversationContext) -> Dict[str, Any]:
        """Диагностика - ИСПРАВЛЕННАЯ ВЕРСИЯ"""

        logger.info(f"🔬 Starting diagnosis for conversation: {context.conversation_id}")
        logger.info(f"   Symptoms: {len(context.symptom_texts)}")
        logger.info(f"   Clarification attempts: {context.clarification_attempts_count}")
        logger.info(f"   Max attempts: {context.max_clarification_attempts}")

        try:
            if "diagnostician" in self.agents:
                # Подготавливаем данные
                diagnosis_data = {
                    "symptoms": context.symptom_texts,
                    "conversation_id": context.conversation_id,
                    "clarification_attempts": context.clarification_attempts_count
                }

                diagnosis_result = await self.agents["diagnostician"].process(diagnosis_data)

                if diagnosis_result and "preliminary_diagnosis" in diagnosis_result:
                    prelim = diagnosis_result["preliminary_diagnosis"]

                    # Сохраняем диагноз
                    from core.conversation_context import DiagnosisInfo
                    diagnosis_info = DiagnosisInfo(
                        name=prelim.get('diagnosis', 'Требуется уточнение'),
                        confidence=prelim.get('confidence', 0.0),
                        differential_diagnosis=prelim.get('differential_diagnosis', []),
                        supporting_evidence=prelim.get('supporting_evidence', []),
                        needs_clarification=prelim.get('needs_clarification', True)
                    )

                    context.primary_diagnosis = diagnosis_info
                    confidence = diagnosis_info.confidence
                    needs_clarification = diagnosis_info.needs_clarification

                    logger.info(f"✅ Diagnosis saved: {diagnosis_info.name} (confidence: {confidence}, needs_clarification: {needs_clarification})")
                    logger.info(f"   Primary diagnosis object: {context.primary_diagnosis}")
                    logger.info(f"   Clarification attempts: {context.clarification_attempts_count}/{context.max_clarification_attempts}")

                    # Проверяем, нужно ли уточнение
                    should_clarify = (
                        (needs_clarification or confidence < 0.7) and 
                        context.clarification_attempts_count < context.max_clarification_attempts
                    )

                    if should_clarify and "clarification_agent" in self.agents:
                        logger.info(f"   🔍 Needs clarification, asking questions...")
                        context.current_stage = ConversationStage.CLARIFICATION
                        
                        # Используем ClarificationAgent для генерации вопросов
                        clarification_result = await self.agents["clarification_agent"].process({
                            "conversation_id": context.conversation_id,
                            "primary_diagnosis": {
                                "diagnosis": diagnosis_info.name,
                                "confidence": confidence
                            },
                            "symptoms": context.symptom_texts,
                            "clarification_attempts": context.clarification_attempts_count,
                            "max_clarification_attempts": context.max_clarification_attempts
                        })
                        
                        clarification_questions = clarification_result.get("clarification_questions", [])
                        
                        if clarification_questions:
                            context.set_clarification_questions(clarification_questions)
                            
                            response = f"🔍 **Предварительный диагноз:** {diagnosis_info.name}\n"
                            response += f"**Уверенность:** {confidence * 100:.0f}%\n\n"
                            response += "Для более точного диагноза, пожалуйста, уточните:\n\n"
                            for i, question in enumerate(clarification_questions, 1):
                                response += f"{i}. {question}\n"
                            
                            context.add_message("assistant", response)
                            
                            return {
                                "response": response,
                                "conversation_id": context.conversation_id,
                                "stage": context.current_stage.value,
                                "needs_input": True,
                                "needs_clarification": True,
                                "clarification_questions": clarification_questions,
                                "diagnosis": diagnosis_info.name,
                                "confidence": confidence
                            }
                        else:
                            # Если не удалось сгенерировать вопросы, переходим к лечению
                            logger.info("   ⚠️ Could not generate clarification questions, proceeding to treatment")
                            should_clarify = False
                    
                    # ЕСЛИ НЕ НУЖНО УТОЧНЕНИЕ - ПЕРЕХОДИМ К ЛЕЧЕНИЮ
                    if not should_clarify:
                        logger.info(f"   💊 Moving to TREATMENT (confidence: {confidence}, attempts: {context.clarification_attempts_count})")
                        context.current_stage = ConversationStage.TREATMENT

                        response = f"🔍 **Диагноз:** {diagnosis_info.name}\n"
                        response += f"**Уверенность:** {confidence * 100:.0f}%\n\n"
                        response += "Подбираю рекомендации по лечению..."

                        context.add_message("assistant", response)

                        # Запускаем подбор лечения СРАЗУ, не асинхронно
                        logger.info("   🚀 Starting treatment immediately...")
                        treatment_result = await self._handle_treatment(context)

                        # Объединяем ответы
                        final_response = response + "\n\n" + treatment_result.get("response", "")

                        return {
                            "response": final_response,
                            "conversation_id": context.conversation_id,
                            "stage": context.current_stage.value,
                            "needs_input": False,
                            "diagnosis": diagnosis_info.name,
                            "confidence": confidence
                        }

            # Fallback
            logger.warning("   ⚠️ Diagnostician failed, using fallback")
            return await self._handle_treatment_fallback(context)

        except Exception as e:
            logger.error(f"Diagnosis failed: {e}", exc_info=True)
            return await self._handle_treatment_fallback(context)

    async def _handle_treatment_fallback(self, context: ConversationContext) -> Dict[str, Any]:
        """Fallback лечение если диагностика не сработала"""
        logger.info("   🩹 Using treatment fallback")

        # Создаем простой диагноз для fallback
        from core.conversation_context import DiagnosisInfo
        symptoms_text = " ".join(context.symptom_texts).lower()

        if "горло" in symptoms_text and "температур" in symptoms_text and "кашель" in symptoms_text:
            diagnosis_name = "Острый фарингит"
            confidence = 0.75
        elif "горло" in symptoms_text and "температур" in symptoms_text:
            diagnosis_name = "Острый фарингит"
            confidence = 0.7
        elif "кашель" in symptoms_text and "температур" in symptoms_text:
            diagnosis_name = "ОРВИ"
            confidence = 0.8
        else:
            diagnosis_name = "Респираторная инфекция"
            confidence = 0.6

        diagnosis_info = DiagnosisInfo(
            name=diagnosis_name,
            confidence=confidence,
            needs_clarification=False
        )

        context.primary_diagnosis = diagnosis_info

        # Переходим к лечению
        context.current_stage = ConversationStage.TREATMENT
        response = f"🔍 **Диагноз:** {diagnosis_name}\nПодбираю рекомендации..."
        context.add_message("assistant", response)

        treatment_result = await self._handle_treatment(context)

        return {
            "response": response + "\n\n" + treatment_result.get("response", ""),
            "conversation_id": context.conversation_id,
            "stage": context.current_stage.value,
            "needs_input": False
        }

    async def _handle_clarification(self, context: ConversationContext, user_input: str) -> Dict[str, Any]:
        """Обработка уточнений - ИСПРАВЛЕННАЯ ВЕРСИЯ"""

        logger.info(f"🔍 Processing clarification for conversation: {context.conversation_id}")
        logger.info(f"   User input: '{user_input[:100]}...'")
        logger.info(f"   Current clarification attempt: {context.clarification_attempts_count}")

        # Добавляем уточнение как симптом
        context.add_symptom(user_input)
        logger.info(f"   Added as symptom. Total symptoms: {len(context.symptom_texts)}")

        # Также добавляем в normalized_symptoms если есть
        if hasattr(context, 'normalized_symptoms'):
            if "symptom_normalizer" in self.agents:
                try:
                    # Нормализуем новое уточнение
                    normalization_result = await self.agents["symptom_normalizer"].process({
                        "symptoms": [user_input],
                        "context": context.to_dict()
                    })

                    if normalization_result and "normalized_symptoms" in normalization_result:
                        # Добавляем к существующим нормализованным симптомам
                        existing = getattr(context, 'normalized_symptoms', [])
                        new_symptoms = normalization_result.get("normalized_symptoms", [])
                        context.normalized_symptoms = existing + new_symptoms

                        logger.info(f"   Added {len(new_symptoms)} normalized symptoms")
                except Exception as e:
                    logger.error(f"   Failed to normalize clarification: {e}")

        # Сбрасываем вопросы уточнения
        context.reset_clarification()

        # ВОЗВРАЩАЕМСЯ К ДИАГНОСТИКЕ (не к симптомам!)
        context.current_stage = ConversationStage.DIAGNOSIS
        logger.info(f"   Returning to DIAGNOSIS stage")

        response = "✅ Спасибо за уточнение. Анализирую с учетом новой информации..."
        context.add_message("assistant", response)

        # Запускаем диагностику заново с обновленными симптомами
        asyncio.create_task(self._handle_diagnosis(context))

        return {
            "response": response,
            "conversation_id": context.conversation_id,
            "stage": context.current_stage.value,
            "needs_input": False
        }

    async def _handle_treatment(self, context: ConversationContext) -> Dict[str, Any]:
        """Подбор лечения - ИСПРАВЛЕННЫЙ"""

        logger.info(f"💊 STARTING TREATMENT for conversation: {context.conversation_id}")
        logger.info(f"   Has primary_diagnosis: {context.primary_diagnosis is not None}")

        if context.primary_diagnosis:
            logger.info(f"   Diagnosis name: {context.primary_diagnosis.name}")
            logger.info(f"   Diagnosis confidence: {context.primary_diagnosis.confidence}")
        else:
            logger.error("   ❌ No primary diagnosis!")

        try:
            # Подбираем лекарства
            if "medicine_provider" in self.agents:
                logger.info(f"   🩺 MedicineProvider found, calling...")

                # Создаем данные для MedicineProvider
                medicine_data = {
                    "primary_diagnosis": context.primary_diagnosis,
                    "symptom_texts": context.symptom_texts,
                    "conversation_id": context.conversation_id,
                    "diagnosis_data": {
                        "diagnosis": context.primary_diagnosis.name if context.primary_diagnosis else "",
                        "confidence": context.primary_diagnosis.confidence if context.primary_diagnosis else 0.0
                    }
                }

                # Добавляем в context для передачи
                context.update(**medicine_data)

                logger.info(f"   📤 Sending to MedicineProvider: {medicine_data}")
                treatment_result = await self.agents["medicine_provider"].process(context)
                logger.info(f"   📥 MedicineProvider result: {treatment_result}")

                if treatment_result and treatment_result.get("recommendation_success", False):
                    # Сохраняем результаты
                    context.update(**treatment_result)

                    # Форматируем финальный ответ
                    if "recommendations_text" in treatment_result:
                        # Используем готовый текст из MedicineProvider
                        final_response = treatment_result["recommendations_text"]
                    else:
                        # Форматируем сами
                        final_response = self._format_final_response(context, treatment_result)

                    context.add_message("assistant", final_response)
                    context.current_stage = ConversationStage.COMPLETED

                    logger.info(f"   ✅ Treatment recommendations generated")

                    return {
                        "response": final_response,
                        "conversation_id": context.conversation_id,
                        "stage": context.current_stage.value,
                        "needs_input": False,
                        "has_recommendations": True
                    }
                else:
                    logger.warning("   ❌ MedicineProvider returned no successful recommendations")

            # Если не удалось подобрать лечение
            logger.warning("   ⚠️ Could not generate treatment recommendations")
            final_response = self._format_fallback_response(context)
            context.add_message("assistant", final_response)
            context.current_stage = ConversationStage.COMPLETED

            return {
                "response": final_response,
                "conversation_id": context.conversation_id,
                "stage": context.current_stage.value,
                "needs_input": False
            }

        except Exception as e:
            logger.error(f"❌ Treatment failed: {e}", exc_info=True)

            final_response = self._format_fallback_response(context)
            context.add_message("assistant", final_response)
            context.current_stage = ConversationStage.COMPLETED

            return {
                "response": final_response,
                "conversation_id": context.conversation_id,
                "stage": context.current_stage.value,
                "needs_input": False
            }

    def _format_final_response(self, context: ConversationContext, treatment_result: Dict) -> str:
        """Форматирует финальный ответ"""

        response = "👋 **Здравствуйте!**\n\n"
        response += "**На основе ваших симптомов и противопоказаний:**\n\n"

        if context.primary_diagnosis:
            response += f"**Предварительный диагноз:** {context.primary_diagnosis.name}\n"
            response += f"**Уверенность в диагнозе:** {context.primary_diagnosis.confidence * 100:.0f}%\n\n"

        response += "**Рекомендации:**\n\n"

        if "suggested_medicines" in treatment_result and treatment_result["suggested_medicines"]:
            medicines = treatment_result["suggested_medicines"]
            for i, med in enumerate(medicines[:3], 1):
                response += f"{i}. **{med.get('name', 'Препарат')}**\n"
                if med.get('dosage'):
                    response += f"   💊 *Дозировка:* {med.get('dosage')}\n"
                if med.get('safety_notes'):
                    response += f"   ⚠️ *Меры предосторожности:* {med.get('safety_notes')}\n"
                response += "\n"
        else:
            response += "**Рекомендуемые препараты:**\n"
            response += "1. **Парацетамол**\n"
            response += "   💊 *Дозировка:* 500 мг каждые 6-8 часов\n"
            response += "   📋 *Применение:* Для снижения температуры и боли\n\n"
            response += "2. **Ибупрофен**\n"
            response += "   💊 *Дозировка:* 200-400 мг каждые 6-8 часов\n"
            response += "   📋 *Применение:* Противовоспалительное и обезболивающее\n\n"

        response += "**Общие рекомендации:**\n"
        response += "• Полоскание горла солевым раствором (1 ч.л. соли на стакан воды)\n"
        response += "• Обильное теплое питье\n"
        response += "• Отдых и покой\n"
        response += "• Увлажнение воздуха в помещении\n\n"

        response += "**Важные указания:**\n"
        response += "• Проконсультируйтесь с врачом перед применением\n"
        response += "• Соблюдайте рекомендации по дозировке\n"
        response += "• При ухудшении состояния обратитесь за помощью\n\n"

        response += "⚠️ **Это предварительная рекомендация. Для получения медицинской помощи обратитесь к специалисту.**"

        return response

    async def _handle_unknown(self, context: ConversationContext) -> Dict[str, Any]:
        """Обрабатывает неизвестное состояние - ИСПРАВЛЕННЫЙ"""

        logger.warning(f"⚠️  Handling UNKNOWN stage for conversation {context.conversation_id}")
        logger.warning(f"   Current stage: {context.current_stage}")
        logger.warning(f"   Symptoms: {len(context.symptom_texts)}")
        logger.warning(
            f"   Has diagnosis: {hasattr(context, 'primary_diagnosis') and context.primary_diagnosis is not None}")

        # СЦЕНАРИЙ 1: Если консультация уже ЗАВЕРШЕНА
        if context.current_stage == ConversationStage.COMPLETED:
            logger.info(f"   Conversation is COMPLETED, showing final recommendations")

            if hasattr(context, 'suggested_medicines') and context.suggested_medicines:
                # Показываем лекарства
                response = "Консультация завершена. Вот рекомендации по лечению:\n\n"
                for i, med in enumerate(context.suggested_medicines[:3], 1):
                    if isinstance(med, dict):
                        response += f"{i}. **{med.get('name', 'Препарат')}**\n"
                        if med.get('dosage'):
                            response += f"   💊 Дозировка: {med.get('dosage')}\n"
                        if med.get('reason'):
                            response += f"   📋 Причина: {med.get('reason')[:50]}...\n"
                        response += "\n"
                response += "⚠️ **Это предварительные рекомендации. Проконсультируйтесь с врачом!**"
            else:
                response = "Консультация завершена. Рекомендую обратиться к врачу для назначения лечения."

            context.add_message("assistant", response)

            return {
                "response": response,
                "conversation_id": context.conversation_id,
                "stage": context.current_stage.value,
                "needs_input": False
            }

        # СЦЕНАРИЙ 2: Если уже есть диагноз и лечение
        elif (hasattr(context, 'primary_diagnosis') and context.primary_diagnosis and
              hasattr(context, 'suggested_medicines') and context.suggested_medicines):
            logger.info(f"   Has diagnosis and treatment, marking as COMPLETED")
            context.current_stage = ConversationStage.COMPLETED

            response = "Консультация завершена. Вот рекомендации по лечению:\n\n"
            for i, med in enumerate(context.suggested_medicines[:3], 1):
                if isinstance(med, dict):
                    response += f"{i}. **{med.get('name', 'Препарат')}**\n"
                    if med.get('dosage'):
                        response += f"   Дозировка: {med.get('dosage')}\n"
                    response += "\n"

            context.add_message("assistant", response)

            return {
                "response": response,
                "conversation_id": context.conversation_id,
                "stage": context.current_stage.value,
                "needs_input": False
            }

        # СЦЕНАРИЙ 3: Если есть диагноз, но нет лечения
        elif hasattr(context, 'primary_diagnosis') and context.primary_diagnosis:
            logger.info(f"   Has diagnosis: {context.primary_diagnosis.name}, moving to TREATMENT")
            context.current_stage = ConversationStage.TREATMENT
            return await self._handle_treatment(context)

        # СЦЕНАРИЙ 4: Если есть симптомы, но нет диагноза
        elif len(context.symptom_texts) > 0:
            logger.info(f"   Has symptoms but no diagnosis, returning to DIAGNOSIS")
            context.current_stage = ConversationStage.DIAGNOSIS
            return await self._handle_diagnosis(context)

        # СЦЕНАРИЙ 5: Если есть противопоказания, но нет симптомов
        elif context.contraindications_collected:
            logger.info(f"   Has contraindications, asking for symptoms")
            response = "Пожалуйста, опишите ваши симптомы."
            context.current_stage = ConversationStage.SYMPTOM_COLLECTION

        # СЦЕНАРИЙ 6: Начинаем сначала
        else:
            logger.info(f"   Starting from beginning")
            return await self._handle_greeting(context)

        context.add_message("assistant", response)

        return {
            "response": response,
            "conversation_id": context.conversation_id,
            "stage": context.current_stage.value,
            "needs_input": True
        }

    def _extract_conversation_id(self, state: Any) -> str:
        """Извлекает ID беседы"""
        conversation_id = self._safe_get(state, 'conversation_id')
        if not conversation_id:
            if hasattr(state, 'conversation_id'):
                conversation_id = getattr(state, 'conversation_id')
        return str(conversation_id) if conversation_id else ""

    def _extract_symptoms_data(self, state: Any) -> Any:
        """Извлекает данные симптомов"""
        if hasattr(state, 'get_symptoms_for_processing'):
            return state.get_symptoms_for_processing()
        elif hasattr(state, 'symptoms'):
            return getattr(state, 'symptoms', [])
        else:
            return self._safe_get(state, 'symptoms', [])

    def _extract_symptoms_text(self, symptoms_data: Any) -> str:
        """Извлекает текст симптомов"""
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
                else:
                    symptoms_text_parts.append(str(symptom))
        elif isinstance(symptoms_data, str):
            symptoms_text_parts.append(symptoms_data)
        else:
            symptoms_text_parts.append(str(symptoms_data))

        return " ".join(symptoms_text_parts)

    def _format_fallback_response(self, context: ConversationContext) -> str:
        """Fallback ответ"""

        response = "👋 **Здравствуйте!**\n\n"
        response += "Проанализировал ваши симптомы.\n\n"

        if context.primary_diagnosis:
            response += f"**Возможный диагноз:** {context.primary_diagnosis.name}\n"
            response += f"**Уверенность:** {context.primary_diagnosis.confidence * 100:.0f}%\n\n"

        response += "**Общие рекомендации:**\n"
        response += "1. Проконсультируйтесь с врачом для точного диагноза\n"
        response += "2. Соблюдайте постельный режим при необходимости\n"
        response += "3. Пейте достаточное количество жидкости\n"
        response += "4. При ухудшении состояния вызовите врача\n\n"

        response += "⚠️ **Для точного диагноза и лечения обратитесь к врачу.**"

        return response