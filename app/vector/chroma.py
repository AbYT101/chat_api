import os
import re
from typing import Optional
from chromadb import PersistentClient
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
from app.vector.base import BaseVectorStore


PERSIST_DIR = "./chroma_db"


class ChromaVectorStore(BaseVectorStore):
    def __init__(self, collection_name: str):
        self._base_collection_name = collection_name
        self._provider = os.getenv("EMBEDDINGS_PROVIDER", "openai").lower()
        if self._provider == "ollama":
            self._model = os.getenv("OLLAMA_EMBEDDINGS_MODEL", "nomic-embed-text")
        else:
            self._model = os.getenv("OPENAI_EMBEDDINGS_MODEL", "text-embedding-3-small")

        self.embeddings = self._build_embeddings(self._provider, self._model)

        self._collection_by_model = (
            os.getenv("EMBEDDINGS_COLLECTION_BY_MODEL", "1").lower()
            in {"1", "true", "yes"}
        )
        self._search_all_collections = (
            os.getenv("EMBEDDINGS_SEARCH_ALL_COLLECTIONS", "1").lower()
            in {"1", "true", "yes"}
        )

        collection = collection_name
        if self._collection_by_model:
            safe_model = re.sub(r"[^a-zA-Z0-9_-]+", "_", self._model)
            safe_provider = re.sub(r"[^a-zA-Z0-9_-]+", "_", self._provider)
            collection = f"{collection_name}__{safe_provider}__{safe_model}"

        self.store = Chroma(
            collection_name=collection,
            embedding_function=self.embeddings,
            persist_directory=PERSIST_DIR,
        )

    def upsert(self, texts, metadatas, ids):
        self.store.add_texts(texts=texts, metadatas=metadatas, ids=ids)

    def similarity_search(self, query, k=5, filter=None):
        scored = self.similarity_search_with_score(query=query, k=k, filter=filter)
        return [doc for doc, _score in scored]
    
    def similarity_search_with_score(self, query, k=5, filter=None):
        if not (self._collection_by_model and self._search_all_collections):
            return self.store.similarity_search_with_score(query=query, k=k, filter=filter)

        collections = self._list_matching_collections()
        if not collections:
            return self.store.similarity_search_with_score(query=query, k=k, filter=filter)

        results = []
        for name in collections:
            provider, model = self._parse_collection_info(name)
            if not provider or not model:
                continue
            if provider == "ollama" and not self._ollama_enabled():
                continue
            embeddings = self._build_embeddings(provider, model)
            store = Chroma(
                collection_name=name,
                embedding_function=embeddings,
                persist_directory=PERSIST_DIR,
            )
            try:
                results.extend(
                    store.similarity_search_with_score(query=query, k=k, filter=filter)
                )
            except ConnectionError:
                # Skip collections that require unavailable backends (e.g., Ollama).
                continue

        if not results:
            return results

        results.sort(key=lambda item: item[1])
        return results[:k]

    def _build_embeddings(self, provider: str, model: str):
        if provider == "ollama":
            return OllamaEmbeddings(model=model)
        return OpenAIEmbeddings(model=model)

    def _list_matching_collections(self) -> list[str]:
        client = PersistentClient(path=PERSIST_DIR)
        base = self._base_collection_name
        names = [col.name for col in client.list_collections()]
        return [
            name
            for name in names
            if name == base or name.startswith(f"{base}__")
        ]

    def _parse_collection_info(self, name: str) -> tuple[Optional[str], Optional[str]]:
        base = self._base_collection_name
        if name.startswith(f"{base}__"):
            parts = name.split("__", 2)
            if len(parts) == 3:
                return parts[1], parts[2]

        if name == base:
            legacy_provider = os.getenv("LEGACY_EMBEDDINGS_PROVIDER", "ollama").lower()
            if legacy_provider == "ollama":
                legacy_model = os.getenv(
                    "LEGACY_OLLAMA_EMBEDDINGS_MODEL", "nomic-embed-text"
                )
            else:
                legacy_model = os.getenv(
                    "LEGACY_OPENAI_EMBEDDINGS_MODEL", "text-embedding-3-small"
                )
            return legacy_provider, legacy_model

        return None, None

    def _ollama_enabled(self) -> bool:
        return os.getenv("OLLAMA_ENABLED", "1").lower() in {"1", "true", "yes"}

