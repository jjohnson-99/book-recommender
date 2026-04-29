from pathlib import Path
from app.worker.celery_app import celery_app
from app.db.session import SessionLocal
from app.services.ingestion_service import process_csv
from app.services.embedding_pipeline import (
        embed_missing_books,
        embed_missing_reviews
)
from app.repositories import upload_repository


@celery_app.task(
    name="app.worker.tasks.process_csv_task",
    bind=True,
    max_retries=3,
)
def process_csv_task(self, upload_id: int) -> None:
    db = SessionLocal()
    try:
        upload = upload_repository.get_upload_by_id(db, upload_id)

        if upload.status == "completed":
            return

        if upload.status == "processing":
            return

        upload_repository.update_status(db, upload_id, "processing")
        db.commit()

        file_path = Path(upload.file_path)

        if not file_path.exists():
            raise self.retry(countdown=1)

        process_csv(db, upload_id)

        upload_repository.update_status(db, upload_id, "completed")
        db.commit()

        embed_books_task.delay()
        embed_reviews_task.delay()

    except Exception as e:
        db.rollback()

        upload_repository.mark_upload_failed(upload_id, str(e))

        raise

    finally:
        db.close()


@celery_app.task
def embed_books_task() -> None:
    db = SessionLocal()
    try:
        embed_missing_books(db)
    finally:
        db.close()


@celery_app.task
def embed_reviews_task() -> None:
    db = SessionLocal()
    try:
        embed_missing_reviews(db)
    finally:
        db.close()
