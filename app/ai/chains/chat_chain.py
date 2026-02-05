import os
import httpx
from typing import AsyncGenerator
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

from app.ai.chains.llm_adapter import RegistryLLM
from app.ai.memory.chat_memory import get_chat_history
from app.ai.prompts.chat_prompt import CHAT_PROMPT
from app.ai.registry import ModelRegistry


class AIChatService:
    """Service for AI-powered chat with conversation memory"""
    
    @staticmethod
    def _default_text_model() -> str:
        return os.getenv("DEFAULT_TEXT_MODEL", "gpt-5-mini")
    
    @staticmethod
    def create_chain(model_name: str):
        llm = RegistryLLM(model_name=model_name)

        # The chain itself (LCEL)
        chain = CHAT_PROMPT | llm

        # Add message history
        chain_with_history = RunnableWithMessageHistory(
            chain,
            # This must return a BaseChatMessageHistory for the session
            get_chat_history,
            input_messages_key="input",
            history_messages_key="history",
        )

        return chain_with_history
    
    @staticmethod
    async def generate_response(
        user_message: str,
        conversation_id: int,
        model_name: str = "gpt-5-mini"
    ) -> str:
        """Generate AI response for a user message"""
        # Use conversation_id as session_id for memory
        try:
            chain = AIChatService.create_chain(model_name)
            response = await chain.ainvoke(
                {"input": user_message},
                config={"configurable": {"session_id": str(conversation_id)}}
            )
        except (ValueError, ConnectionError, httpx.ConnectError):
            fallback = AIChatService._default_text_model()
            if fallback == model_name:
                raise
            chain = AIChatService.create_chain(fallback)
            response = await chain.ainvoke(
                {"input": user_message},
                config={"configurable": {"session_id": str(conversation_id)}}
            )
        
        return response
    
    @staticmethod
    async def generate_response_stream(
        user_message: str,
        conversation_id: int,
        model_name: str = "gpt-5-mini"
    ) -> AsyncGenerator[str, None]:
        """Generate AI response with streaming"""
        # Get conversation history
        session_id = str(conversation_id)
        chat_history = get_chat_history(session_id)
        
        # Build history string from messages
        messages = chat_history.get_messages()
        history_text = ""
        for msg in messages:
            if isinstance(msg, HumanMessage):
                history_text += f"User: {msg.content}\n"
            elif isinstance(msg, AIMessage):
                history_text += f"Assistant: {msg.content}\n"
        
        # Format the full prompt with history
        prompt_text = CHAT_PROMPT.format(history=history_text, input=user_message)
        
        full_response = ""

        async def stream_from_model(selected_model: str):
            nonlocal full_response
            llm = ModelRegistry.get_text_model(selected_model)
            try:
                async for chunk in llm.generate_stream(prompt_text):
                    full_response += chunk
                    yield chunk
            except NotImplementedError:
                full_response = await llm.generate(prompt_text)
                if full_response:
                    yield full_response

        try:
            async for chunk in stream_from_model(model_name):
                yield chunk
        except (ValueError, ConnectionError, httpx.ConnectError):
            fallback = AIChatService._default_text_model()
            if fallback == model_name:
                raise
            full_response = ""
            async for chunk in stream_from_model(fallback):
                yield chunk
        
        # Save to message history after streaming completes
        chat_history.add_message(HumanMessage(content=user_message))
        chat_history.add_message(AIMessage(content=full_response))
