from typing import Dict, Any, Optional
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from contextlib import asynccontextmanager
import os
import asyncio

logger = logging.getLogger(__name__)


class FrontendMessage(BaseModel):
    message: str
    chat: int
    method: str = "content"
    top_n: int = 5

    @property
    def conversation_id(self) -> str:
        return str(self.chat)


class FrontendResponse(BaseModel):
    chatId: int
    response: str
    success: bool = True


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


orchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global orchestrator

    logger.info("Starting Medical Assistant API for frontend...")

    try:
        from utils.ollama_client import OllamaClient
        from config.settings import get_settings

        settings = get_settings()

        ollama_client = OllamaClient(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=settings.OLLAMA_TEMPERATURE,
            timeout=settings.OLLAMA_TIMEOUT
        )

        if not ollama_client.is_available():
            logger.warning("Ollama не доступен, используем заглушки")
            ollama_client = None

        agents = await initialize_agents(ollama_client)

        from core.agent_orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator(agents)

        logger.info(f"✅ Medical Assistant initialized with {len(agents)} agents")

    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
        from core.agent_orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator({})

    yield

    logger.info("Shutting down Medical Assistant API...")


app = FastAPI(
    title="Medical Assistant API",
    description="API для фронтенда медицинского ассистента",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/v1/chat", response_model=FrontendResponse)
async def frontend_chat(message: FrontendMessage):
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        logger.info(f"📨 Frontend request: chat={message.chat}, message='{message.message[:50]}...'")

        result = await asyncio.wait_for(
            orchestrator.process_conversation(
                conversation_id=message.conversation_id,
                user_input=message.message
            ),
            timeout=1145.0
        )

        response_text = result.get("response", "Извините, не удалось обработать запрос.")

        if len(response_text) > 4000:
            response_text = response_text[:4000] + "..."

        response_data = {
            "chatId": message.chat,
            "response": response_text,
            "success": True
        }

        logger.info(f"Frontend response for chat {message.chat}: {len(response_text)} chars")

        return FrontendResponse(**response_data)

    except asyncio.TimeoutError:
        logger.error(f"Frontend chat timeout for chat: {message.chat}")
        return FrontendResponse(
            chatId=message.chat,
            response="Извините, обработка запроса заняла слишком много времени. Попробуйте еще раз.",
            success=False
        )

    except Exception as e:
        logger.error(f"Frontend chat error for chat {message.chat}: {e}", exc_info=True)
        return FrontendResponse(
            chatId=message.chat,
            response="Произошла ошибка при обработке запроса. Попробуйте еще раз.",
            success=False
        )


@app.post("/api/chat", response_model=AssistantResponse)
async def chat(message: UserMessage):
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        result = await orchestrator.process_conversation(
            conversation_id=message.conversation_id,
            user_input=message.text
        )
        return AssistantResponse(**result)

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return AssistantResponse(
            response="Произошла ошибка при обработке запроса. Попробуйте еще раз.",
            conversation_id=message.conversation_id or "unknown",
            stage="error",
            needs_input=True
        )


@app.get("/")
async def root():
    return {
        "service": "Medical Assistant API",
        "version": "1.0.0",
        "status": "running",
        "frontend_endpoint": "/api/v1/chat",
        "description": "API для фронтенда медицинского ассистента"
    }


@app.get("/api/health")
async def health_check():
    health_info = {
        "status": "healthy",
        "orchestrator": orchestrator is not None,
        "success": True
    }

    if orchestrator:
        health_info["conversations"] = len(orchestrator.conversations)
        health_info["agents"] = len(orchestrator.agents)

    return health_info


async def initialize_agents(llm_client):
    agents = {}

    try:
        from agents.diagnostician import Diagnostician
        from agents.medicine_provider import MedicineProvider
        from agents.symptom_normalizer import SymptomNormalizer
        from agents.contraindications_collector import ContraindicationsCollector
        from agents.clarification_agent import ClarificationAgent

        agents["diagnostician"] = Diagnostician(llm_client)
        agents["medicine_provider"] = MedicineProvider(
            llm_client,
            medicine_data_path=os.path.join('data', 'medicines_ru_top500.json')
        )
        agents["symptom_normalizer"] = SymptomNormalizer(llm_client)
        agents["contraindications_collector"] = ContraindicationsCollector(llm_client)
        agents["clarification_agent"] = ClarificationAgent(llm_client)

        logger.info(f"Initialized {len(agents)} agents for frontend")

    except ImportError as e:
        logger.warning(f"Some agents not available: {e}")
        from agents.base_agent import BaseAgent

        class FastAgent(BaseAgent):
            def __init__(self, name):
                super().__init__(name, llm_client)

            async def process(self, state):
                return {"status": f"{self.name} processed"}

        agents["diagnostician"] = FastAgent("Diagnostician")
        agents["medicine_provider"] = FastAgent("MedicineProvider")

        logger.info(f"Created {len(agents)} fast agents")

    except Exception as e:
        logger.error(f"Failed to initialize agents: {e}")

    return agents


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
        uvicorn.run(
            "api.fastapi_app:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        )