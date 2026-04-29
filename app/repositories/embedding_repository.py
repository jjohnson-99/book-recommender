from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from app.models import Book


def update_book_embedding(
    db: Session,
    book_id: int,
    embedding: List[float]
) -> None:
    db.execute(
        text("""
            UPDATE books
            SET embedding = :embedding
            WHERE id = :book_id
        """),
        {
            "book_id": book_id,
            "embedding": embedding
        }
    )


def search_similar_books(
    db: Session,
    query_embedding: List[float],
    limit: int = 5
) -> List[Book]:
    result = db.execute(
        text("""
            SELECT
                b.id,
                b.title,
                b.author
            FROM books b
            LEFT JOIN reviews r ON b.id = r.book_id
            GROUP BY b.id, b.title, b.author
            ORDER BY
                (b.embedding <-> CAST(:embedding AS vector))
                -- (COALESCE(AVG(r.rating), 0) * 0.02)
            LIMIT :limit
        """),
        {
            "embedding": query_embedding,
            "limit": limit
        }
    )

    rows = result.mappings().all()
    return [Book(**row) for row in rows]

def get_books_without_embeddings(db: Session) -> List[Book]:
    result = db.execute(
        text("""
            SELECT id, title, author
            FROM books
            WHERE embedding IS NULL
        """))

    rows = result.mappings().all()
    return [Book(**row) for row in rows]


def update_review_embedding(
        db: Session,
        review_id: int,
        embedding: List[float]
) -> None:
    db.execute(
        text("""
            UPDATE reviews
            SET embedding = :embedding
            WHERE id = :id
        """),
        {"id": review_id, "embedding": embedding}
    )


def get_user_review_embeddings(
    db: Session,
    user_id: int
) -> List[dict]:
    result = db.execute(text("""
        SELECT embedding, rating
        FROM reviews
        WHERE user_id = :user_id
          AND embedding IS NOT NULL
    """), {"user_id": user_id})

    return result.mappings().all()


