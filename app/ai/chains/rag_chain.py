from typing import List, Optional
from app.ai.prompts.rag_prompt import prompt_template
from app.ai.chains.llm_adapter import RegistryLLM
from app.vector.chroma import ChromaVectorStore


class RAGService:
    @staticmethod
    def build_context(docs) -> str:
        return "\n\n".join([doc.page_content for doc in docs])

    @staticmethod
    async def run(
        question: str,
        user_id: int,
        model_name: str,
        k: int = 5,
        ingestion_types: Optional[List[str]] = None,
    ) -> str:
        """
        Run RAG query with optional filtering by ingestion type.
        
        Args:
            question: User's question
            user_id: User ID for filtering
            model_name: LLM model name
            k: Number of results to retrieve
            ingestion_types: List of ingestion types to search (e.g., ["file", "image", "text"])
                           If None, searches all types
        """
        # Use unified collection
        store = ChromaVectorStore(collection_name="unified_docs")

        # Build filter
        # ChromaDB requires multiple conditions to be wrapped in $and
        if ingestion_types:
            filter_dict = {
                "$and": [
                    {"user_id": user_id},
                    {"ingestion_type": {"$in": ingestion_types}}
                ]
            }
        else:
            filter_dict = {"user_id": user_id}

        docs = store.similarity_search(query=question, k=k, filter=filter_dict)

        context = RAGService.build_context(docs)

        llm = RegistryLLM(model_name=model_name)

        chain = prompt_template | llm

        result = await chain.ainvoke({"context": context, "question": question})

        return result
