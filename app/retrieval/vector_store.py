import chromadb
from typing import List
from app.ingestion.chunker import Chunk
from app.retrieval.embedder import Embedder


class VectorStore:
    """
    Stores and retrieves embeddings using Chroma DB.
    """

    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(name="banking_rag")
        self.embedder = Embedder()

    def add_chunks(self, chunks: List[Chunk]):
        texts = [chunk.content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]

        embeddings = self.embedder.encode(texts)

        ids = [f"{i}" for i in range(len(chunks))]

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

    def search(self, query: str, top_k: int = 3):
        query_embedding = self.embedder.encode([query])[0]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        return results