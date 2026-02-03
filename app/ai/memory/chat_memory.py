from typing import List
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage

# Store message history per session
_message_store = {}


class InMemoryChatMessageHistory(BaseChatMessageHistory):
    """In-memory implementation of chat message history"""
    
    def __init__(self):
        self.messages: List[BaseMessage] = []
    
    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the history"""
        self.messages.append(message)
    
    async def aadd_messages(self, messages: List[BaseMessage]) -> None:
        """Add messages to the history (async version)"""
        self.messages.extend(messages)
    
    def clear(self) -> None:
        """Clear all messages from history"""
        self.messages = []
    
    def get_messages(self) -> List[BaseMessage]:
        """Get all messages from history"""
        return self.messages
    
    async def aget_messages(self) -> List[BaseMessage]:
        """Get all messages from history (async version)"""
        return self.messages


def get_chat_history(session_id: str) -> BaseChatMessageHistory:
    """Get or create chat message history for a session"""
    if session_id not in _message_store:
        _message_store[session_id] = InMemoryChatMessageHistory()
    return _message_store[session_id]
