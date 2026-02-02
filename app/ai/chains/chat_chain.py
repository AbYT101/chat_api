from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import MessagesPlaceholder

from app.ai.chains.llm_adapter import RegistryLLM
from app.ai.memory.chat_memory import build_memory
from app.ai.prompts.chat_prompt import CHAT_PROMPT


class ChatService:
    @staticmethod
    def create_chain(model_name: str):
        llm = RegistryLLM(model_name=model_name)

        # The chain itself (LCEL)
        chain = CHAT_PROMPT | llm

        # Add message history
        chain_with_history = RunnableWithMessageHistory(
            chain,
            # This must return the SAME memory object for the same session/thread/user
            lambda session_id: build_memory(
                session_id=session_id
            ),  # ← most important change
            input_messages_key="input",
            history_messages_key="history",
        )

        return chain_with_history
