from sqlalchemy.orm import Session
from fastapi import APIRouter, UploadFile, File, Depends
from app.services import upload_service
from app.db.session import get_db
from typing import Dict, Any
import sys

router = APIRouter()

@router.post("/uploads")
def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    return upload_service.create_upload(db, file)
