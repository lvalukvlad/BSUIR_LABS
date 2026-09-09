from abc import ABC, abstractmethod
from typing import Union


class BaseParser(ABC):

    @abstractmethod
    def parse(self, content: bytes) -> str:
        pass

    @abstractmethod
    def get_supported_extensions(self) -> list[str]:
        pass