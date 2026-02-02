from langchain_core.prompts import PromptTemplate

CHAT_PROMPT = PromptTemplate(
    input_variables=["history", "input"],
    template="""
You are a helpful AI assistant having a conversation with a user.

Conversation history:
{history}

User message:
{input}

Respond naturally, helpfully, and concisely.
""",
)
