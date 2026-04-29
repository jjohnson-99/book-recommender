import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from typing import Generator

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@db:5432/books"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
