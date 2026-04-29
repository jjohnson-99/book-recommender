import json
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from app.models import Book
from app.services.normalization import normalize_text, canonical_author
from app.repositories import ingestion_log_repository



def get_or_create_book(
    db: Session,
    title: str,
    author: Optional[str],
    additional_authors: Optional[str],
    upload_id: Optional[int] = None
) -> Book:
    norm_title = normalize_text(title)
    norm_author = canonical_author(author)

    # Try insert first (safe with ON CONFLICT)
    result = db.execute(
        text("""
            INSERT INTO books (
                title, author,
                additional_authors,
                normalized_title, normalized_author
            )
            VALUES (
                :title, :author,
                :additional_authors,
                :norm_title, :norm_author
            )
            ON CONFLICT DO NOTHING
            RETURNING *
        """),
        {
            "title": title,
            "author": author,
            "additional_authors": additional_authors,
            "norm_title": norm_title,
            "norm_author": norm_author
        }
    )

    row = result.mappings().first()

    if row:
        return Book(**row)

    # Conflict → fetch existing
    result = db.execute(
        text("""
            SELECT * FROM books
            WHERE normalized_title = :title
              AND (
                  normalized_author = :author
                  OR (:author IS NULL AND normalized_author IS NULL)
              )
            LIMIT 1
        """),
        {"title": norm_title, "author": norm_author}
    )

    row = result.mappings().first()
    message = f"dedup hit: '{title}' by '{author}' -> book_id={row['id']}"

    if upload_id:
        ingestion_log_repository.log_ingestion(
            upload_id,
            step="dedup",
            message=json.dumps({
                "message": message,
            })
        )

    return Book(**row)

