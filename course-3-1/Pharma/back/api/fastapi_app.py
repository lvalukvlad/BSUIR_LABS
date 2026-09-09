from typing import Dict, Any, Optional
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from contextlib import asynccontextmanager
import os
logger = logging.getLogger(__name__)


# Модели запросов/ответов
class UserMessage(BaseModel):
    text: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None


class AssistantResponse(BaseModel):
    response: str
    conversation_id: str
    stage: str
    needs_input: bool = True
    needs_clarification: bool = False
    clarification_questions: Optional[list] = None
    structured_response: Optional[Dict[str, Any]] = None


class ConversationHistory(BaseModel):
    conversation_id: str
    messages: list
    created_at: str
    updated_at: str


class WorkflowRequest(BaseModel):
    workflow_name: str = Field(default="full")
    initial_data: Dict[str, Any] = Field(default_factory=dict)


class WorkflowResponse(BaseModel):
    workflow_id: str
    status: str
    results: Dict[str, Any]
    duration: Optional[float] = None


# Глобальные объекты
orchestrator = None
ollama_client = None


def create_fallback_agent(agent_name: str):
    """Создает агент-заглушку"""

    class DummyLLM:
        async def generate(self, *args, **kwargs):
            return f"{agent_name}: Сервис временно недоступен"

        async def chat(self, *args, **kwargs):
            return f"{agent_name}: Сервис временно недоступен"

    from agents.base_agent import BaseAgent

    class FallbackAgent(BaseAgent):
        def __init__(self, name):
            super().__init__(name=name, llm_client=DummyLLM())

        async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
            state[f"{self.name}_fallback"] = True
            return state

    return FallbackAgent(agent_name)


async def initialize_agents(llm_client) -> Dict[str, Any]:
    agents = {}

    try:
        from agents.contraindications_collector import ContraindicationsCollector
        agents["contraindications_collector"] = ContraindicationsCollector(llm_client)
        logger.info("✓ ContraindicationsCollector initialized")
    except ImportError as e:
        logger.error(f"✗ Failed to import ContraindicationsCollector: {e}")

    try:
        from agents.diagnostician import Diagnostician
        agents["diagnostician"] = Diagnostician(llm_client)
        logger.info("✓ Diagnostician initialized")
    except ImportError as e:
        logger.error(f"✗ Failed to import Diagnostician: {e}")
        agents["diagnostician"] = create_fallback_agent("Diagnostician")

    try:
        from agents.localization_expert import LocalizationExpert
        agents["localization_expert"] = LocalizationExpert(llm_client)
        logger.info("✓ LocalizationExpert initialized")
    except ImportError as e:
        logger.error(f"✗ Failed to import LocalizationExpert: {e}")
        agents["localization_expert"] = create_fallback_agent("LocalizationExpert")

    try:
        from agents.symptom_normalizer import SymptomNormalizer
        agents["symptom_normalizer"] = SymptomNormalizer(llm_client)
        logger.info("✓ SymptomNormalizer initialized")
    except ImportError as e:
        logger.error(f"✗ Failed to import SymptomNormalizer: {e}")
        agents["symptom_normalizer"] = create_fallback_agent("SymptomNormalizer")

    try:
        from agents.clarification_agent import ClarificationAgent
        agents["clarification_agent"] = ClarificationAgent(llm_client)
        logger.info("✓ ClarificationAgent initialized")
    except ImportError as e:
        logger.error(f"✗ Failed to import ClarificationAgent: {e}")
        agents["clarification_agent"] = create_fallback_agent("ClarificationAgent")

    # В fastapi_app.py обновить инициализацию MedicineProvider
    try:
        from agents.medicine_provider import MedicineProvider
        # Используем большой датасет
        medicine_db_path = os.path.join('data', 'medicines_ru_full.json')  # Или medicines.csv
        agents["medicine_provider"] = MedicineProvider(
            llm_client=llm_client,
            medicine_data_path=medicine_db_path,
            use_similarity_search=True
        )
        logger.info(f"✓ MedicineProvider initialized with dataset: {medicine_db_path}")
    except ImportError as e:
        logger.error(f"✗ Failed to import MedicineProvider: {e}")
        agents["medicine_provider"] = create_fallback_agent("MedicineProvider")

    logger.info(f"✅ Total initialized: {len(agents)} agents")
    return agents


async def initialize_fallback_mode():
    """Инициализация в режиме без Ollama"""
    logger.info("Initializing fallback mode...")

    class FallbackLLM:
        async def generate(self, prompt, system_prompt=None, max_tokens=1000):
            return "Обработка запроса временно недоступна. Пожалуйста, попробуйте позже."

        async def chat(self, messages, max_tokens=1000):
            return "Обработка запроса временно недоступна. Пожалуйста, попробуйте позже."

    fallback_client = FallbackLLM()
    agents = await initialize_agents(fallback_client)

    # Ленивый импорт AgentOrchestrator
    from core.agent_orchestrator import AgentOrchestrator
    return AgentOrchestrator(agents)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan контекст для инициализации и завершения"""
    global orchestrator, ollama_client

    # Startup
    logger.info("Starting Medical Assistant API...")

    try:
        from utils.ollama_client import OllamaClient
        from config.settings import get_settings

        settings = get_settings()

        # Инициализация Ollama клиента
        ollama_client = OllamaClient(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=settings.OLLAMA_TEMPERATURE,
            timeout=settings.OLLAMA_TIMEOUT
        )

        # Проверка доступности Ollama
        if not ollama_client.is_available():
            logger.error("Ollama is not available! Please start Ollama server.")
            # Можно продолжить с заглушкой
            raise RuntimeError("Ollama server is not available")

        logger.info(f"Ollama client initialized with model: {settings.OLLAMA_MODEL}")

        # Инициализация агентов
        agents = await initialize_agents(ollama_client)

        # Инициализация оркестратора
        from core.agent_orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator(agents)

        logger.info("Medical Assistant initialized successfully")

    except ImportError as e:
        logger.error(f"Import error: {e}")
        orchestrator = await initialize_fallback_mode()
    except Exception as e:
        logger.error(f"Failed to initialize Medical Assistant: {e}")
        # Инициализируем с заглушками для тестирования
        orchestrator = await initialize_fallback_mode()

    yield

    # Shutdown
    logger.info("Shutting down Medical Assistant API...")
    # Очистка ресурсов


# Инициализация приложения с lifespan
app = FastAPI(
    title="Medical Assistant API",
    description="AI медицинский ассистент для диагностики и рекомендаций",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "service": "Medical Assistant API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "chat": "/api/chat",
            "conversations": "/api/conversations/{conversation_id}",
            "health": "/api/health",
            "workflows": "/api/workflows"
        }
    }


@app.get("/api/health")
async def health_check():
    """Проверка здоровья сервиса"""
    health_info = {
        "status": "healthy",
        "ollama": ollama_client.health_check() if ollama_client else {"available": False},
        "orchestrator": orchestrator is not None
    }

    if orchestrator:
        health_info["conversations"] = len(orchestrator.conversations)
        health_info["agents"] = len(orchestrator.agents)

    # Детальная проверка
    if ollama_client and not ollama_client.is_available():
        health_info["status"] = "degraded"
        health_info["message"] = "Ollama server is not available"

    return health_info


@app.post("/api/v1/chat", response_model=AssistantResponse)
@app.post("/api/chat", response_model=AssistantResponse)  # Для обратной совместимости
async def chat(message: UserMessage):
    """Основной endpoint для общения с ассистентом"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # Обрабатываем сообщение
        result = await orchestrator.process_conversation(
            conversation_id=message.conversation_id,
            user_input=message.text
        )

        # Всегда возвращаем ответ, даже если пустой
        return AssistantResponse(**result)

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        # Возвращаем сообщение об ошибке
        return AssistantResponse(
            response="Произошла ошибка при обработке запроса. Попробуйте еще раз.",
            conversation_id=message.conversation_id or "unknown",
            stage="error",
            needs_input=True
        )


@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Получение истории беседы"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Service not initialized")

    conversation = orchestrator.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    history = orchestrator.get_conversation_history(conversation_id)

    return ConversationHistory(
        conversation_id=conversation_id,
        messages=history,
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat()
    )


@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Удаление диалога"""
    if conversation_id in orchestrator.conversations:
        del orchestrator.conversations[conversation_id]
        return {"status": "deleted", "conversation_id": conversation_id}
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")

@app.get("/api/workflows")
async def list_workflows():
    """Список доступных workflow"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Service not initialized")

    workflows = []
    if hasattr(orchestrator, 'workflow_engine'):
        workflows = list(orchestrator.workflow_engine.workflows.keys()) if hasattr(orchestrator.workflow_engine, 'workflows') else []

    return {
        "workflows": workflows,
        "descriptions": {
            "full": "Полный медицинский workflow (сбор симптомов → диагностика → лечение)",
            "diagnosis": "Только диагностика",
            "treatment": "Только лечение (требует диагноза)",
            "symptom_collection": "Сбор и нормализация симптомов",
            "quick": "Быстрая диагностика с оценкой серьезности"
        }
    }


@app.get("/api/stats")
async def get_stats():
    """Статистика сервиса"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Service not initialized")

    return {
        "conversations_total": len(orchestrator.conversations),
        "agents_total": len(orchestrator.agents),
        "active_conversations": len([c for c in orchestrator.conversations.values() if c.current_stage != "completed"])
    }


if __name__ == "__main__":
    try:
        from config.settings import get_settings

        settings = get_settings()

        uvicorn.run(
            "api.fastapi_app:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=True
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        # Запуск с настройками по умолчанию
        uvicorn.run(
            "api.fastapi_app:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        )