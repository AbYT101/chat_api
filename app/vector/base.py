from abc import ABC, abstractmethod
from typing import Optional, List, Any, Dict


class BaseVectorStore(ABC):

    @abstractmethod
    def upsert(self, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        pass

    @abstractmethod
    def similarity_search(
        self, query: str, k: int = 5, where: Dict[str, Any] | None = None
    ):
        pass
