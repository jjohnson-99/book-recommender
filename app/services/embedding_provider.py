from typing import List
from openai import OpenAI
from sentence_transformers import SentenceTransformer


class EmbeddingProvider:
    def embed(self, text: str) -> List[float]:
        raise NotImplementedError


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self) -> None:
        self.client = OpenAI()
        self.model = "text-embedding-3-small"

    def embed(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding


class LocalEmbeddingProvider(EmbeddingProvider):
    def __init__(self) -> None:
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()
