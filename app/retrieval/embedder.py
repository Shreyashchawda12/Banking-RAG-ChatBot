from sentence_transformers import SentenceTransformer
from typing import List


class Embedder:
    """
    Converts text into embeddings.
    """

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def encode(self, texts: List[str]) -> List[List[float]]:
        """
        Convert list of texts into embeddings.
        """
        return self.model.encode(texts).tolist()