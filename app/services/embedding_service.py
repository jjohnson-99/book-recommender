from typing import Optional, List
from app.services.embedding_provider import (
        LocalEmbeddingProvider,
        OpenAIEmbeddingProvider
)

#provider = OpenAIEmbeddingProvider()
provider = LocalEmbeddingProvider()


def build_book_text(
    title: str,
    authors: Optional[str],
) -> str:
    parts = []

    if title:
        parts.append(f"Title: {title}")

    if authors:
        parts.append(f"Authors: {authors}")

    return "\n".join(parts)


def generate_embedding(text: str) -> List[float]:
    return provider.embed(text)


def average_embeddings(embeddings: List[List[float]]) -> List[float]:
    return [
        sum(values) / len(values) for values in zip(*embeddings)
    ]


def build_user_embedding(rows: List[dict]) -> List[float]:
    weighted: List[List[float]] = []

    for r in rows:
        weight = (r["rating"] or 0) / 5
        weighted.append([x * weight for x in r["embedding"]])

    return average_embeddings(weighted)
