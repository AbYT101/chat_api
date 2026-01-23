from app.ai.ollama import OllamaLLM, OllamaVisionLLM
from app.ai.base import BaseLLM, BaseVisionLLM


class ModelRegistry:
    _TEXT_MODELS = {
        "llama3.2:3b": lambda: OllamaLLM("llama3.2:3b"),
        "mistral": lambda: OllamaLLM("mistral"),
    }

    _VISION_MODELS = {"llava": lambda: OllamaVisionLLM("llava")}

    @classmethod
    def get_text_model(cls, model_name: str) -> BaseLLM:
        if model_name not in cls._TEXT_MODELS:
            raise ValueError(f"Unsupported text model: {model_name}")

        return cls._TEXT_MODELS[model_name]()

    @classmethod
    def get_vision_model(cls, model_name: str) -> BaseVisionLLM:
        if model_name not in cls._VISION_MODELS:
            raise ValueError(f"Unsupported vision model: {model_name}")

        return cls._VISION_MODELS[model_name]()

    @classmethod
    def list_models(cls):
        return {
            "text": list(cls._TEXT_MODELS.keys()),
            "vision": list(cls._VISION_MODELS.keys()),
        }
