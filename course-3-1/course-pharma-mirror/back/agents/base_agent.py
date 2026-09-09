from typing import Any, Dict, Optional, Union
from abc import ABC, abstractmethod
import logging
import asyncio
import datetime
import inspect
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Базовый агент с зависимостью от LLM"""

    def __init__(self, name: Optional[str] = None, llm_client=None):
        self.name = name or self.__class__.__name__
        self.llm = llm_client
        self.logger = logging.getLogger(f"agent.{self.name}")

        if not self.llm:
            raise ValueError(f"Agent {self.name} requires LLM client")

    @abstractmethod
    async def process(self, state: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
        """Основной метод обработки. Должен быть реализован в подклассах."""
        raise NotImplementedError

    async def generate_with_llm(self,
                                prompt: str,
                                system_prompt: Optional[str] = None,
                                max_tokens: int = 1000) -> Optional[str]:
        """Генерация через LLM"""
        try:
            self.logger.debug(f"Generating with {self.name}, prompt length: {len(prompt)}")

            if not system_prompt:
                system_prompt = "Будь кратким и точным. Ответь в указанном формате."

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt[:500]})
            messages.append({"role": "user", "content": prompt[:2000]})

            # КРИТИЧЕСКО ВАЖНО: Проверяем тип llm
            self.logger.debug(f"LLM client type: {type(self.llm)}")
            self.logger.debug(f"LLM has chat method: {hasattr(self.llm, 'chat')}")

            # Используем chat API если есть
            if hasattr(self.llm, 'chat'):
                # Проверяем является ли chat асинхронным методом
                import inspect
                is_coroutine = inspect.iscoroutinefunction(self.llm.chat)
                self.logger.debug(f"chat method is coroutine: {is_coroutine}")

                if is_coroutine:
                    # Асинхронный вызов
                    response = await self.llm.chat(messages, max_tokens=max_tokens)
                else:
                    # Синхронный вызов
                    response = self.llm.chat(messages, max_tokens=max_tokens)

                self.logger.debug(f"Chat response type: {type(response)}")
                self.logger.debug(f"Chat response first 100 chars: {str(response)[:100] if response else 'None'}")
                return response
            else:
                # Fallback на generate
                self.logger.debug("Using generate fallback")
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

                if hasattr(self.llm, 'generate'):
                    if inspect.iscoroutinefunction(self.llm.generate):
                        response = await self.llm.generate(full_prompt, max_tokens=max_tokens)
                    else:
                        response = self.llm.generate(full_prompt, max_tokens=max_tokens)
                    return response

            self.logger.error("No suitable LLM method found")
            return None

        except asyncio.TimeoutError:
            self.logger.error(f"LLM timeout in {self.name} after {max_tokens} tokens")
            return None
        except Exception as e:
            self.logger.error(f"LLM generation failed in {self.name}: {e}", exc_info=True)
            return None

    def _safe_get(self, state: Any, key: str, default: Any = None) -> Any:
        """Безопасное получение значения из состояния любого типа"""
        if isinstance(state, dict):
            return state.get(key, default)
        elif hasattr(state, key):
            return getattr(state, key, default)
        elif hasattr(state, 'to_dict'):
            state_dict = state.to_dict()
            return state_dict.get(key, default)
        return default

    def _safe_to_dict(self, state: Any) -> Dict[str, Any]:
        """Безопасное преобразование состояния в словарь"""
        if isinstance(state, dict):
            return state.copy()
        elif hasattr(state, 'to_dict'):
            return state.to_dict()
        elif isinstance(state, (str, int, float, bool)):
            return {"value": state}
        else:
            try:
                return dict(state)
            except:
                return {"raw_state": str(state)}

    def _extract_data(self, state: Any, *keys: str, default: Any = None) -> Any:
        """Извлекает данные по цепочке ключей из состояния любого типа"""
        current = state

        for key in keys:
            if isinstance(current, dict):
                current = current.get(key, default)
            elif hasattr(current, key):
                current = getattr(current, key, default)
            elif hasattr(current, 'to_dict'):
                current_dict = current.to_dict()
                current = current_dict.get(key, default)
            else:
                return default

            if current is None:
                return default

        return current

    async def __call__(self, state: Any) -> Dict[str, Any]:
        """Вызов агента как функции"""
        try:
            # Обрабатываем состояние
            result = await self.process(state)

            # Добавляем метаданные
            if isinstance(result, dict):
                result["agent"] = self.name
                result["agent_timestamp"] = datetime.datetime.now().isoformat()
                result["agent_success"] = True
            else:
                # Если результат не словарь, оборачиваем его
                result = {
                    "result": result,
                    "agent": self.name,
                    "agent_timestamp": datetime.datetime.now().isoformat(),
                    "agent_success": True
                }

            self.logger.debug(f"Agent {self.name} completed successfully")
            return result

        except Exception as e:
            self.logger.error(f"Agent {self.name} failed: {e}", exc_info=True)

            # Создаем результат с ошибкой
            error_result = {
                "agent": self.name,
                "agent_timestamp": datetime.datetime.now().isoformat(),
                "agent_success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }

            # Безопасно добавляем данные из состояния
            try:
                state_dict = self._safe_to_dict(state)
                error_result["input_data"] = state_dict
            except Exception as dict_error:
                self.logger.debug(f"Failed to convert state to dict: {dict_error}")
                error_result["input_type"] = str(type(state))

            return error_result