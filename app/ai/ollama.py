import httpx
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
                f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=60
            )

            resp.raise_for_status()
            return resp.json()["response"]


class OllamaVisionLLM(OllamaLLM, BaseVisionLLM):
    async def describe_image(self, image_bytes: bytes, prompt: str | None = None):
        payload = {
            "model": self.model,
            "prompt": prompt or "Describe this image in detail.",
            "images": [image_bytes.hex()],
            "stream": False,
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate", payload, timeout=120
            )

            resp.raise_for_status()
            return resp.json()["response"]
