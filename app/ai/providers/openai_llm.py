import asyncio
from typing import Optional, AsyncGenerator
from langchain_openai import ChatOpenAI

from app.ai.base import BaseLLM


class OpenAILLM(BaseLLM):
    model_name: str

    def __init__(self, model_name: str):
        self.model_name = model_name
        self._client = ChatOpenAI(
            model=model_name,
            temperature=0.2,
        )

    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
    ) -> str:
        input_text = prompt if not context else f"{context} \n\n {prompt}"
        if hasattr(self._client, "ainvoke"):
            result = await self._client.ainvoke(input_text)
            return getattr(result, "content", result)
        if hasattr(self._client, "invoke"):
            result = await asyncio.to_thread(self._client.invoke, input_text)
            return getattr(result, "content", result)
        if hasattr(self._client, "apredict"):
            return await self._client.apredict(input_text)
        return await asyncio.to_thread(self._client.predict, input_text)

    async def generate_stream(
        self,
        prompt: str,
        context: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        input_text = prompt if not context else f"{context} \n\n {prompt}"
        if hasattr(self._client, "astream"):
            async for chunk in self._client.astream(input_text):
                content = getattr(chunk, "content", "")
                if content:
                    yield content
            return

        yield await self.generate(prompt, context=context)
