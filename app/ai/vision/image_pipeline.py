from uuid import uuid4
from app.ai.registry import ModelRegistry
from app.vector.chroma import ChromaVectorStore


class ImageIngestionService:

    @staticmethod
    async def ingest(
        image_bytes: bytes,
        user_id: int,
        conversation_id: int | None = None,
        model_name: str = "llava",
        filename: str = "uploaded_image",
    ):
        """Process image with vision model and store in unified vector database"""
        # Vision model
        vision_llm = ModelRegistry.get_vision_model(model_name)

        description = await vision_llm.describe_image(
            image_bytes=image_bytes,
            prompt="Describe the objects, text, and key information in this image in detail.",
        )

        # Store in unified VectorDB with ingestion_type metadata
        store = ChromaVectorStore(collection_name="unified_docs")

        store.upsert(
            texts=[description],
            metadatas=[
                {
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "ingestion_type": "image",
                    "source": filename,
                }
            ],
            ids=[str(uuid4())],
        )

        return description
