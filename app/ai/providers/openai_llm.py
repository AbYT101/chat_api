import asyncio
import base64
import imghdr
from typing import Optional, AsyncGenerator
from langchain_openai import ChatOpenAI
from openai import OpenAI

from app.ai.base import BaseLLM, BaseVisionLLM


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


class OpenAIVisionLLM(BaseVisionLLM):
    model_name: str

    def __init__(self, model_name: str):
        self.model_name = model_name
        self._client = OpenAI()

    async def describe_image(
        self,
        image_bytes: bytes,
        prompt: Optional[str] = None,
        content_type: Optional[str] = None,
    ) -> str:
        if not image_bytes:
            raise ValueError("Image upload is empty.")

        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
        }
        mime = content_type if content_type in allowed_types else None
        if not mime:
            detected = imghdr.what(None, h=image_bytes)
            mapping = {
                "jpeg": "image/jpeg",
                "png": "image/png",
                "gif": "image/gif",
                "webp": "image/webp",
            }
            mime = mapping.get(detected)
        if not mime:
            raise ValueError(
                "Unsupported image type. Please upload jpg, png, gif, or webp."
            )

        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        message = {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": prompt or "Describe this image in detail.",
                },
                {
                    "type": "input_image",
                    "image_url": f"data:{mime};base64,{image_b64}",
                },
            ],
        }

        def _call():
            return self._client.responses.create(
                model=self.model_name,
                input=[message],
            )

        response = await asyncio.to_thread(_call)
        if hasattr(response, "output_text"):
            return response.output_text

        # Fallback for older response shapes
        for output in getattr(response, "output", []):
            for content in getattr(output, "content", []):
                text = getattr(content, "text", None)
                if text:
                    return text

        return ""
