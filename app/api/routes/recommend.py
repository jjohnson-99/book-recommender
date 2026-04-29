from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.services.embedding_service import (
    generate_embedding,
    build_user_embedding,
)
from app.repositories.embedding_repository import (
    search_similar_books,
    get_user_review_embeddings,
)
from app.models import (
    Book,
    RecommendRequest,
)
from app.utils.retry import retry

router = APIRouter()


@router.post("/recommend")
def recommend(req: RecommendRequest, db: Session = Depends(get_db)) -> List[Book]:
    try:
        query_embedding = retry(
                lambda: generate_embedding(req.query),
                exceptions=(TimeoutError, ConnectionError),
                retries=3,
                delay=0.5,
                backoff=2.0
        )

        rows = get_user_review_embeddings(db, user_id=req.user_id)

        if rows:
            user_embedding = build_user_embedding(rows)

            final_embedding = query_embedding
            #final_embedding = [
            #    (q * 0.9 + u * 0.1) / 2 for q, u in zip(query_embedding, user_embedding)
            #]
        else:
            final_embedding = query_embedding

        results = search_similar_books(db, final_embedding, limit=req.limit)

        return results

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
