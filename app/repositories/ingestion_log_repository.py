from sqlalchemy import text
from app.db.session import SessionLocal


def log_ingestion(
    upload_id: int,
    step: str,
    message: str
) -> None:
    db = SessionLocal()
    try:
        db.execute(
            text("""
                INSERT INTO ingestion_logs (upload_id, step, message)
                VALUES (:upload_id, :step, :message)
            """),
            {
                "upload_id": upload_id,
                "step": step,
                "message": message
            }
        )
        db.commit()
    except Exception:
        pass
    finally:
        db.close()
