import os
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import UploadFile
from typing import Dict
from app.repositories import upload_repository
from app.services import ingestion_service
from app.worker.tasks import process_csv_task

UPLOAD_DIR = Path("data/uploads")


def save_file(file: UploadFile) -> str:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return str(file_path)


def create_upload(
        db: Session,
        file: UploadFile,
        user_id: int = 1
) -> Dict:
    file_path = save_file(file)

    upload = upload_repository.create_upload(
        db=db,
        user_id=user_id,
        filename=file.filename,
        file_path=file_path
    )

    db.commit()

    print("About to enqueue task")
    process_csv_task.delay(upload.id)
    print("Task enqueued")

    return {
        "upload_id": upload.id,
        "status": upload.status
    }


