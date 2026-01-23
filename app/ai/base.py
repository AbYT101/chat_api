from abc import ABC, abstractmethod
from typing import Optional, List


class BaseLLM(ABC):
    @abstractmethod
    def generate(self, prompt: str, context: Optional[str] = None) -> str:
        pass


class BaseVisionLLM(ABC):
    @abstractmethod
    def describe_image(self, image_bytes: bytes, prompt: Optional[str] = None) -> str:
        pass
