from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from app.models import Review


def create_review(
    db: Session,
    user_id: int,
    book_id: int,
    upload_id: int,
    rating: Optional[int],
    review_text: Optional[str],
    date_read: Optional[str]
) -> Review:
    result = db.execute(
        text("""
            INSERT INTO reviews (
                user_id, book_id, upload_id,
                rating, review_text, date_read
            )
            VALUES (
                :user_id, :book_id, :upload_id,
                :rating, :review_text, :date_read
            )
            ON CONFLICT (user_id, book_id)
            DO UPDATE SET
                rating = EXCLUDED.rating,
                review_text = EXCLUDED.review_text,
                date_read = EXCLUDED.date_read
            WHERE
                reviews.date_read IS NULL
                OR (
                    EXCLUDED.date_read IS NOT NULL
                    AND EXCLUDED.date_read > reviews.date_read
                )
            RETURNING *
        """),
        {
            "user_id": user_id,
            "book_id": book_id,
            "upload_id": upload_id,
            "rating": rating,
            "review_text": review_text,
            "date_read": date_read
        }
    )

    row = result.mappings().first()
    if row:
        return Review(**row)

    # fallback: fetch existing row
    result = db.execute(
        text("""
            SELECT * FROM reviews
            WHERE user_id = :user_id AND book_id = :book_id
        """),
        {"user_id": user_id, "book_id": book_id}
    )

    row = result.mappings().first()
    return Review(**row)


