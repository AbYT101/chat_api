from app.ai.prompts.rag_prompt import prompt_template
from app.ai.chains.llm_adapter import RegistryLLM
from app.vector.chroma import ChromaVectorStore


class RAGService:
    @staticmethod
    def build_context(docs) -> str:
        return "\n\n".join([doc.page_content for doc in docs])

    @staticmethod
    async def run(question: str, user_id: int, model_name: str, k: int = 5) -> str:
        store = ChromaVectorStore(collection_name="file_docs")

        docs = store.similarity_search(query=question, k=k, filter={"user_id": user_id})

        context = RAGService.build_context(docs)

        llm = RegistryLLM(model_name=model_name)

        chain = prompt_template | llm

        result = await chain.ainvoke({"context": context, "question": question})

        return result
