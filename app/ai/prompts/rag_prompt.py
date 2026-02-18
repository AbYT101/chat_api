from langchain_core.prompts import ChatPromptTemplate

prompt_template = ChatPromptTemplate(
    [
        (
            "system",
            "You are a helpful AI assistant. "
            "Use ONLY the information provided in the context below to answer the question. "
            "If the answer is not contained in the context, say clearly: "
            "'I don't have enough information to answer that.'\n\n"
            "Context:\n{context}\n\n"
            "Question:\n{question}\n\n"
            "Answer (concise, factual, grounded):",
        )
    ]
)


