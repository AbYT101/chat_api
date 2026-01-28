from langchain_core.language_models.llms import BaseLLM
from langchain_core.language_models.llms import LLMResult
from langchain_core.callbacks import CallbackManagerForLLMRun
from typing import Optional, List, Any
import asyncio
from app.ai.registry import ModelRegistry


class RegistryLLM(BaseLLM):
    model_name: str

    def __init__(self, model_name: str):
        super().__init__(model_name=model_name)
        self._llm = ModelRegistry.get_text_model(model_name)

    @property
    def _llm_type(self) -> str:
        return "registry_llm"

    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Generate LLM result from a list of prompts."""
        # This should not be called from an async context
        # Use _agenerate instead
        raise RuntimeError(
            "RegistryLLM._generate() cannot be called from a running event loop. "
            "This typically happens when using FastAPI/async. "
            "Use an async wrapper or restructure to use ainvoke()."
        )

    async def _agenerate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Async version of generate for use in async contexts"""
        from langchain_core.language_models.llms import Generation

        generations = []
        for prompt in prompts:
            result = await self._llm.generate(prompt)
            generations.append([Generation(text=result)])

        return LLMResult(generations=generations)
