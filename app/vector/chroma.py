from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from app.vector.base import BaseVectorStore


PERSIST_DIR = "./chroma_db"


class ChromaVectorStore(BaseVectorStore):
    def __init__(self, collection_name: str):
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")

        self.store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=PERSIST_DIR,
        )

    def upsert(self, texts, metadatas, ids):
        self.store.add_texts(texts=texts, metadatas=metadatas, ids=ids)

    def similarity_search(self, query, k=5, filter=None):
        return self.store.similarity_search(query=query, k=k, filter=filter)
    
    def similarity_search_with_score(self, query, k=5, filter=None):
        return self.store.similarity_search_with_score(query=query, k=k, filter=filter)

