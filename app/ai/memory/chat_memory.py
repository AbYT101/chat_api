from langchain.memory import ConversationBufferMemory


def build_memory():
    return ConversationBufferMemory(
        memory_key="history",
        input_key="input",
        return_messages=False,
    )
