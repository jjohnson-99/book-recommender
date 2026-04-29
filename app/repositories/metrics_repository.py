from sqlalchemy import text
from app.db.session import SessionLocal


def insert_metrics(
    upload_id: int,
    total_rows: int,
    processed_rows: int,
    skipped_unread: int,
    skipped_invalid: int,
    duration_ms: int
) -> None:
    db = SessionLocal()
    try:
        db.execute(
            text("""
                INSERT INTO ingestion_metrics (
                    upload_id,
                    total_rows,
                    processed_rows,
                    skipped_unread,
                    skipped_invalid,
                    duration_ms
                )
                VALUES (
                    :upload_id,
                    :total_rows,
                    :processed_rows,
                    :skipped_unread,
                    :skipped_invalid,
                    :duration_ms
                )
            """),
            {
                "upload_id": upload_id,
                "total_rows": total_rows,
                "processed_rows": processed_rows,
                "skipped_unread": skipped_unread,
                "skipped_invalid": skipped_invalid,
                "duration_ms": duration_ms,
            }
        )
        db.commit()
    finally:
        db.close()
