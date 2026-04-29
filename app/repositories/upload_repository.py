from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import Upload
from app.db.session import SessionLocal


def create_upload(
    db: Session,
    user_id: int,
    filename: str,
    file_path: str
) -> Upload:
    result = db.execute(
        text("""
            INSERT INTO uploads (user_id, filename, file_path, status)
            VALUES (:user_id, :filename, :file_path, 'pending')
            RETURNING *
        """),
        {
            "user_id": user_id,
            "filename": filename,
            "file_path": file_path
        }
    )

    row = result.mappings().first()

    return Upload(**row)


def get_upload_by_id(
    db: Session,
    upload_id: int
) -> Optional[Upload]:
    result = db.execute(
        text("SELECT * FROM uploads WHERE id = :id"),
        {"id": upload_id}
    )

    row = result.mappings().first()
    return Upload(**row) if row else None


def update_status(
    db: Session,
    upload_id: int,
    status: str,
    error_message: Optional[str] = None
) -> None:
    db.execute(
        text("""
            UPDATE uploads
            SET status = :status,
                error_message = :error_message,
                updated_at = NOW()
            WHERE id = :id
        """),
        {
            "id": upload_id,
            "status": status,
            "error_message": error_message
        }
    )


def update_progress(
    db: Session,
    upload_id: int,
    row_idx: int
) -> None:
    db.execute(
        text("""
            UPDATE uploads
            SET last_processed_row = :row_idx,
                updated_at = NOW()
            WHERE id = :id
        """),
        {
            "id": upload_id,
            "row_idx": row_idx
        }
    )


def mark_upload_failed(upload_id: int, error_message: str) -> None:
    db = SessionLocal()
    try:
        db.execute(
            text("""
                UPDATE uploads
                SET status = 'failed',
                    error_message = :error_message,
                    updated_at = NOW()
                WHERE id = :upload_id
            """),
            {
                "upload_id": upload_id,
                "error_message": error_message
            }
        )
        db.commit()
    finally:
        db.close()

