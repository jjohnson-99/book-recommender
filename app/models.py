from pydantic import BaseModel
from typing import Optional


class Upload(BaseModel):
    id: int
    user_id: int
    filename: str
    file_path: str
    status: str
    last_processed_row: int
    error_message: Optional[str] = None


class Book(BaseModel):
    id: int
    title: str
    author: Optional[str] = None


class Review(BaseModel):
    id: int
    user_id: int
    book_id: int
    upload_id: int
    rating: Optional[int] = None
    review_text: Optional[str] = None


class IngestionLog(BaseModel):
    id: int
    upload_id: int
    step: str
    message: str


class RecommendRequest(BaseModel):
    query: str
    user_id: int = 1
    limit: int = 5
