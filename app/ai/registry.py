from app.ai.ollama import OllamaLLM, OllamaVisionLLM
from app.ai.base import BaseLLM, BaseVisionLLM
from app.ai.providers.openai_llm import OpenAILLM, OpenAIVisionLLM
from app.ai.providers.groq_llm import GroqLLM

class ModelRegistry:
    _TEXT_MODELS = {
        "llama3.2:3b": lambda: OllamaLLM("llama3.2:3b"),
        "mistral": lambda: OllamaLLM("mistral"),
        
        # OpenAI
        "gpt-3.5": lambda: OpenAILLM("gpt-3.5-turbo"),
        "gpt-4o-mini": lambda: OpenAILLM("gpt-4o-mini"),
        "gpt-5-mini": lambda: OpenAILLM("gpt-5-mini"),

        # Groq (FAST)
        "llama3-70b-groq": lambda: GroqLLM("llama3-70b-8192"),
        "mixtral-groq": lambda: GroqLLM("mixtral-8x7b-32768"),
    }

    _VISION_MODELS = {
        "llava": lambda: OllamaVisionLLM("llava"),
        "gpt-4o-mini": lambda: OpenAIVisionLLM("gpt-4o-mini"),
    }
    _OLLAMA_TEXT_MODELS = {"llama3.2:3b", "mistral"}
    _OLLAMA_VISION_MODELS = {"llava"}

    @classmethod
    def get_text_model(cls, model_name: str) -> BaseLLM:
        if model_name not in cls._TEXT_MODELS:
            raise ValueError(f"Unsupported text model: {model_name}")
        if model_name in cls._OLLAMA_TEXT_MODELS and not cls._ollama_enabled():
            raise ValueError(
                "Ollama is disabled or not running. "
                "Choose an OpenAI model or set OLLAMA_ENABLED=1."
            )

        return cls._TEXT_MODELS[model_name]()

    @classmethod
    def get_vision_model(cls, model_name: str) -> BaseVisionLLM:
        if model_name not in cls._VISION_MODELS:
            raise ValueError(f"Unsupported vision model: {model_name}")
        if model_name in cls._OLLAMA_VISION_MODELS and not cls._ollama_enabled():
            raise ValueError(
                "Ollama is disabled or not running. "
                "Choose an OpenAI vision model or set OLLAMA_ENABLED=1."
            )

        return cls._VISION_MODELS[model_name]()

    @classmethod
    def list_models(cls):
        return {
            "text": list(cls._TEXT_MODELS.keys()),
            "vision": list(cls._VISION_MODELS.keys()),
        }

    @staticmethod
    def _ollama_enabled() -> bool:
        from os import getenv
        return getenv("OLLAMA_ENABLED", "1").lower() in {"1", "true", "yes"}
