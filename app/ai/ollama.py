import base64
import httpx
import json
from typing import AsyncGenerator
from app.ai.base import BaseLLM, BaseVisionLLM

OLLAMA_BASE_URL = "http://localhost:11434"


class OllamaLLM(BaseLLM):
    def __init__(self, model: str):
        self.model = model

    async def generate(self, prompt: str, context: str | None = None) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt if not context else f"{context} \n\n {prompt}",
            "stream": False,
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=360
            )

            resp.raise_for_status()
            return resp.json()["response"]
    
    async def generate_stream(
        self, 
        prompt: str, 
        context: str | None = None
    ) -> AsyncGenerator[str, None]:
        """Generate response with streaming"""
        payload = {
            "model": self.model,
            "prompt": prompt if not context else f"{context} \n\n {prompt}",
            "stream": True,
        }

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=360
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                        except json.JSONDecodeError:
                            continue


class OllamaVisionLLM(OllamaLLM, BaseVisionLLM):
    async def describe_image(self, image_bytes: bytes, prompt: str | None = None):
        payload = {
            "model": self.model,
            "prompt": prompt or "Describe this image in detail.",
            "images": [base64.b64encode(image_bytes).decode("utf-8")],
            "stream": False,
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=900
            )

            resp.raise_for_status()
            return resp.json()["response"]
