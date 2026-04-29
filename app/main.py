from fastapi import FastAPI
from app.api.routes.uploads import router as uploads_router
from app.api.routes.recommend import router as recommend_router

app = FastAPI(title="Book Recommendation API")

app.include_router(uploads_router)
app.include_router(recommend_router)
