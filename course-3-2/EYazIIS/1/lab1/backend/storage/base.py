from abc import ABC, abstractmethod
from typing import List, Optional, Any


class BaseStorage(ABC):

    @abstractmethod
    def save(self, entries: List[Any]) -> bool:
        pass

    @abstractmethod
    def load(self) -> List[Any]:
        pass

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        pass

    @abstractmethod
    def search(self, query: str, filters: Optional[dict] = None) -> List[Any]:
        pass