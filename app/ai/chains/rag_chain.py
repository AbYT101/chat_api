import logging
from typing import List, Optional
from app.ai.prompts.rag_prompt import prompt_template
from app.ai.chains.llm_adapter import RegistryLLM
from app.vector.chroma import ChromaVectorStore

logger = logging.getLogger(__name__)

CONTEXT_PREVIEW_LEN = 500


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
        """
        store = ChromaVectorStore(collection_name="unified_docs")

        all_types = {"file", "image", "text"}
        use_type_filter = (
            ingestion_types is not None
            and set(ingestion_types) != all_types
        )
        if use_type_filter:
            filter_dict = {
                "$and": [
                    {"user_id": {"$eq": user_id}},
                    {"ingestion_type": {"$in": ingestion_types}}
                ]
            }
        else:
            filter_dict = {"user_id": {"$eq": user_id}}

        docs = store.similarity_search(query=question, k=k, filter=filter_dict)
        context = RAGService.build_context(docs)

        # Debug logging only
        preview = (context[:CONTEXT_PREVIEW_LEN] + "…") if len(context) > CONTEXT_PREVIEW_LEN else (context or "(empty)")
        logger.info(
            "RAG retrieval: question=%r user_id=%s docs_count=%s context_len=%s filter=%s",
            question[:80], user_id, len(docs), len(context), filter_dict,
        )
        logger.info(
            "RAG context_preview: %s",
            preview,
        )
        if not docs:
            logger.warning("RAG: no documents retrieved for user_id=%s filter=%s", user_id, filter_dict)
        else:
            logger.info(
                "RAG first_doc_metadata: %s",
                docs[0].metadata,
            )

        llm = RegistryLLM(model_name=model_name)
        chain = prompt_template | llm
        result = await chain.ainvoke({"context": context, "question": question})

        if hasattr(result, "content"):
            return result.content
        return str(result)
