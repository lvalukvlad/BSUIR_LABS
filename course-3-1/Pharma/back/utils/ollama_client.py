import requests
import json
from typing import Optional, Dict, Any, List
import time
import logging

logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(self,
                 base_url: str = "http://localhost:11435",
                 model: str = "mistral:latest",
                 temperature: float = 0.7,
                 timeout: int = 1300):

        self.base_url = base_url.rstrip('/')
        self.model = model
        self.temperature = temperature
        self.timeout = timeout

        logger.info(f"Initialized OllamaClient: {base_url}, model: {model}")

    def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}{endpoint}"

        try:
            logger.debug(f"Making request to {url}")
            logger.debug(f"Payload: {json.dumps(payload, ensure_ascii=False)[:200]}...")

            start_time = time.time()
            response = requests.post(url, json=payload, timeout=self.timeout)
            elapsed_time = time.time() - start_time

            logger.debug(f"Response received in {elapsed_time:.2f}s, status: {response.status_code}")

            response.raise_for_status()
            result = response.json()

            return result

        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error to Ollama at {self.base_url}")
            return None
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout to Ollama (>{self.timeout}s)")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error from Ollama: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in Ollama request: {e}")
            return None

    def generate(self,
                 prompt: str,
                 system_prompt: Optional[str] = None,
                 max_tokens: int = 2000) -> Optional[str]:

        logger.info(f"Generating with model {self.model}, prompt length: {len(prompt)}")

        # Упрощенный, более быстрый промпт
        if not system_prompt:
            system_prompt = "Будь кратким и точным. Отвечай только суть."

        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "temperature": self.temperature,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "repeat_penalty": 1.1,
                "top_k": 20,  # Уменьшил для скорости
                "top_p": 0.8,  # Уменьшил для скорости
                "num_thread": 4  # Используем больше потоков
            }
        }

        result = self._make_request("/api/generate", payload)

    async def chat(self,
                   messages: List[Dict[str, str]],
                   max_tokens: int = 2000) -> Optional[str]:
        """Асинхронный метод chat"""

        logger.info(f"Chatting with model {self.model}, messages: {len(messages)}")

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "repeat_penalty": 1.1,
                "top_k": 40,
                "top_p": 0.9
            }
        }

        # Используем асинхронный HTTP клиент
        import aiohttp
        import asyncio

        url = f"{self.base_url}/api/chat"

        try:
            logger.debug(f"Making async request to {url}")
            start_time = time.time()

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(url, json=payload) as response:
                    elapsed_time = time.time() - start_time
                    logger.debug(f"Response received in {elapsed_time:.2f}s, status: {response.status}")

                    response.raise_for_status()
                    result = await response.json()

                    if result:
                        message = result.get("message", {})
                        response_text = message.get("content", "")
                        total_duration = result.get("total_duration", 0) / 1_000_000_000
                        token_count = result.get("eval_count", 0)

                        logger.info(f"Chat completed: {token_count} tokens in {total_duration:.2f}s")
                        logger.debug(f"Response preview: {response_text[:200]}...")

                        return response_text

                    return None

        except asyncio.TimeoutError:
            logger.error(f"Request timeout to Ollama (>{self.timeout}s)")
            return None
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return None

    def is_available(self) -> bool:

        try:
            logger.debug(f"Checking Ollama availability at {self.base_url}")
            response = requests.get(f"{self.base_url}/api/tags", timeout=1500)

            if response.status_code == 200:
                logger.info(f"Ollama is available at {self.base_url}")
                return True
            else:
                logger.warning(f"Ollama returned status {response.status_code}")
                return False

        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Ollama at {self.base_url}")
            return False
        except Exception as e:
            logger.error(f"Error checking Ollama availability: {e}")
            return False

    def list_models(self) -> List[str]:

        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=1110)
            response.raise_for_status()

            data = response.json()
            models = [model["name"] for model in data.get("models", [])]

            logger.info(f"Found {len(models)} models: {', '.join(models)}")
            return models

        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []

    def generate_structured_response(self,
                                     prompt: str,
                                     system_prompt: Optional[str] = None,
                                     max_tokens: int = 2000) -> Optional[str]:

        if not system_prompt:
            system_prompt = """Ты - опытный врач-диагност. 
            Твои ответы должны быть:
            1. На русском языке
            2. Профессиональными и точными
            3. Структурированными и понятными
            4. Использовать медицинскую терминологию
            5. Включать рекомендации по дальнейшим действиям

            Форматируй ответы с использованием эмодзи и маркированных списков для наглядности."""

        logger.info(f"Generating structured medical response")
        return self.generate(prompt, system_prompt, max_tokens)

    def get_embedding(self, text: str) -> Optional[List[float]]:

        logger.info(f"Getting embedding for text of length {len(text)}")

        payload = {
            "model": self.model,
            "prompt": text
        }

        result = self._make_request("/api/embeddings", payload)

        if result:
            embedding = result.get("embedding", [])
            logger.info(f"Embedding generated: {len(embedding)} dimensions")
            return embedding

        return None

    def pull_model(self, model_name: str) -> bool:

        logger.info(f"Pulling model {model_name}")

        payload = {
            "name": model_name,
            "stream": False
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json=payload,
                timeout=1300
            )

            if response.status_code == 200:
                logger.info(f"Model {model_name} pulled successfully")
                return True
            else:
                logger.error(f"Failed to pull model {model_name}: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error pulling model {model_name}: {e}")
            return False

    def get_model_info(self) -> Optional[Dict[str, Any]]:

        try:
            response = requests.get(f"{self.base_url}/api/show", params={"name": self.model}, timeout=1100)
            response.raise_for_status()

            model_info = response.json()
            logger.info(f"Model info retrieved for {self.model}")
            return model_info

        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return None

    def health_check(self) -> Dict[str, Any]:

        health_info = {
            "available": False,
            "models": [],
            "current_model": self.model,
            "base_url": self.base_url
        }

        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=1500)

            if response.status_code == 200:
                health_info["available"] = True

                data = response.json()
                models = [model["name"] for model in data.get("models", [])]
                health_info["models"] = models

                health_info["current_model_available"] = self.model in models

                logger.info(f"Health check passed: {len(models)} models available")
            else:
                logger.warning(f"Health check failed: status {response.status_code}")

        except Exception as e:
            logger.error(f"Health check error: {e}")

        return health_info