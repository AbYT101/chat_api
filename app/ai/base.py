from abc import ABC, abstractmethod
from typing import Optional, List, AsyncGenerator


class BaseLLM(ABC):
    @abstractmethod
    async def generate(self, prompt: str, context: Optional[str] = None) -> str:
        pass

    async def generate_stream(
        self, prompt: str, context: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        raise NotImplementedError("Streaming is not supported for this model.")


class BaseVisionLLM(ABC):
    @abstractmethod
    def describe_image(
        self,
        image_bytes: bytes,
        prompt: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> str:
        pass
