import asyncio
import os
from typing import Optional, AsyncGenerator
from groq import Groq

from app.ai.base import BaseLLM


class GroqLLM(BaseLLM):
    model_name: str

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
    ) -> str:
        input_text = prompt if not context else f"{context} \n\n {prompt}"

        def _call():
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": input_text}],
            )
            return completion.choices[0].message.content

        return await asyncio.to_thread(_call)

    async def generate_stream(
        self,
        prompt: str,
        context: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        yield await self.generate(prompt, context=context)
