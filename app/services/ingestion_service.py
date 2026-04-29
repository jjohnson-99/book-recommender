import csv
import json
import time
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List
from app.services.embedding_service import (
    build_book_text,
    generate_embedding
)
from app.services.normalization import canonical_author
from app.repositories import (
        book_repository,
        embedding_repository,
        review_repository,
        upload_repository,
        ingestion_log_repository,
        metrics_repository
)
from app.utils.retry import retry


def safe_int(value: Optional[str]) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def clean_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    return value if value else None


def is_read_book(rating: Optional[str], date_read: Optional[str]) -> bool:
    return (rating is not None and rating > 0) or (date_read is not None)


def process_csv(db: Session, upload_id: int) -> None:
    upload = upload_repository.get_upload_by_id(db, upload_id)
    file_path = Path(upload.file_path)

    total_rows = 0
    processed_rows = 0
    skipped_unread = 0
    skipped_invalid = 0

    start_time = time.perf_counter()

    try:
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            for i, row in enumerate(reader, start=1):
                if i <= upload.last_processed_row:
                    continue
                if i % 50 == 0:
                    row_start = time.perf_counter()

                total_rows += 1

                with db.begin_nested():
                    try:
                        title = clean_text(row.get("Title"))
                        author = clean_text(row.get("Author"))
                        additional_authors = clean_text(row.get("Additional Authors"))

                        rating = safe_int(row.get("My Rating"))
                        review_text = clean_text(row.get("My Review"))
                        date_read = clean_text(row.get("Date Read"))

                        if not title:
                            skipped_invalid += 1
                            continue

                        if not is_read_book(rating, date_read):
                            skipped_unread += 1
                            continue

                        book = book_repository.get_or_create_book(
                            db,
                            title=title,
                            author=author,
                            additional_authors=additional_authors,
                            upload_id=upload_id
                        )

                        review_repository.create_review(
                            db,
                            user_id=upload.user_id,
                            book_id=book.id,
                            upload_id=upload_id,
                            rating=rating if rating > 0 else None,
                            date_read=date_read,
                            review_text=review_text
                        )

                        upload_repository.update_progress(db, upload_id, i)

                        if i % 50 == 0:
                            row_duration = int((time.perf_counter() - row_start) * 1000)

                            ingestion_log_repository.log_ingestion(
                                upload_id,
                                step="row_timing",
                                message=json.dumps({
                                    "row_index": i,
                                    "duration_ms": row_duration
                                })
                            )

                        processed_rows += 1

                    except SQLAlchemyError as db_error:
                        skipped_invalid += 1,

                        ingestion_log_repository.log_ingestion(
                            upload_id,
                            step="db_error",
                            message=json.dumps({
                                "row_index": i,
                                "error": str(db_error),
                                "title": title,
                                "author": author,
                            })
                        )

                        continue

                    except Exception as logic_error:
                        ingestion_log_repository.log_ingestion(
                            upload_id,
                            step="fatal_row_error",
                            message=json.dumps({
                                "row_index": i,
                                "error": str(logic_error),
                                "title": title,
                                "author": author,
                            })
                        )

                        raise

        db.commit()

        duration_ms = int((time.perf_counter() - start_time) * 1000)

        metrics_repository.insert_metrics(
            upload_id=upload_id,
            total_rows=total_rows,
            processed_rows=processed_rows,
            skipped_unread=skipped_unread,
            skipped_invalid=skipped_invalid,
            duration_ms=duration_ms
        )

        ingestion_log_repository.log_ingestion(
            upload_id,
            step="summary",
            message=json.dumps({
                "total_rows": total_rows,
                "processed_rows": processed_rows,
                "skipped_unread": skipped_unread,
                "skipped_invalid": skipped_invalid,
            })
        )

    except Exception as e:
        db.rollback()

        upload_repository.mark_upload_failed(upload_id, str(e))

        ingestion_log_repository.log_ingestion(
            upload_id,
            step="fatal",
            message=json.dumps({
                "error": str(e),
                "stage": "process_csv"
            })
        )

        raise
