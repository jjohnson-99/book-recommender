from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.embedding_repository import (
    get_books_without_embeddings,
    update_book_embedding,
)
from app.services.embedding_service import (
    build_book_text,
    generate_embedding,
)
from app.services.normalization import canonical_author
from app.utils.retry import retry


def merge_authors(
    author: Optional[str],
    additional_authors: List[str]
) -> str:
    authors = []

    if author:
        authors.append(author)

    for a in additional_authors:
        if a:
            authors.append(a)

    seen = set()
    deduped = []
    for a in authors:
        if a not in seen:
            seen.add(a)
            deduped.append(a)

    return ", ".join(deduped)


def embed_missing_books(db: Session) -> None:
    books = get_books_without_embeddings(db)

    for book in books:
        additional_authors_list = [
            canonical_author(a)
            for a in book.additional_authors.split(",")
            if a and a.strip()
        ] if additional_raw else []

        merged_authors = merge_authors(book.norm_author, additional_authors_list)

        text = build_book_text(
            title=book.norm_title,
            authors=merged_authors,
        )

        embedding = retry(
                lambda: generate_embedding(text),
                exceptions=(TimeoutError, ConnectionError),
                retries=3,
                delay=0.5,
                backoff=2.0
        )

        update_book_embedding(db, book.id, embedding)


def embed_missing_reviews(db: Session) -> None:
    reviews = get_reviews_without_embeddings(db)

    for review in reviews:
        if not review.review_text:
            continue

        embedding = retry(
            lambda: generate_embedding(review.review_text),
            exceptions=(TimeoutError, ConnectionError),
            retries=3,
            delay=0.5,
            backoff=2.0
        )

        update_review_embedding(db, review.id, embedding)
