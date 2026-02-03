from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate

from app.ai.chains.llm_adapter import RegistryLLM
from app.ai.memory.chat_memory import get_chat_history
from app.ai.prompts.chat_prompt import CHAT_PROMPT


class AIChatService:
    """Service for AI-powered chat with conversation memory"""
    
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
        model_name: str = "llama3.2:3b"
    ) -> str:
        """Generate AI response for a user message"""
        chain = AIChatService.create_chain(model_name)
        
        # Use conversation_id as session_id for memory
        response = await chain.ainvoke(
            {"input": user_message},
            config={"configurable": {"session_id": str(conversation_id)}}
        )
        
        return response
