# Book Recommender

A backend system for ingesting personal reading data and generating semantic book recommendations using embeddings and vector similarity.

**Status:** Work in progress. Core ingestion and retrieval pipeline is functional but still evolving in terms of recommendation quality, data enrichment, and system robustness.

---

## Overview

This project ingests book and review data (e.g., Goodreads exports), processes and normalizes it, generates embeddings, and stores them in a PostgreSQL database with vector support. Recommendations are generated via similarity search over embeddings, optionally incorporating user preferences.

The system is designed as a modular pipeline with clear separation between API, service logic, repository layer, and background workers.

---

## Current Capabilities

- CSV ingestion pipeline (Goodreads export format)
- Data cleaning and normalization (titles, authors, ratings, dates)
- Deduplication of books
- Review storage with conflict resolution ("latest read wins")
- Embedding generation (local model)
- Vector storage using PostgreSQL + pgvector
- Semantic search using cosine distance (`<->`)
- Basic recommendation endpoint
- Background processing with Celery
- Row-level fault tolerance (savepoints)
- Retry logic for transient failures (e.g., embedding generation)
- Structured logging and ingestion metrics

---

## Architecture

### High-level flow:
```
Client → FastAPI → Service Layer → Repository Layer → PostgreSQL
↓
Celery Worker
↓
Ingestion + Embedding Pipeline
```

### Layers

- **API Layer**: FastAPI endpoints (`/uploads`, `/recommend`)
- **Service Layer**: Orchestration, transaction boundaries
- **Repository Layer**: Raw SQL + Pydantic models
- **Worker Layer**: Asynchronous ingestion and embedding tasks
- **Database**: PostgreSQL with pgvector extension

---

## Tech Stack

- Python 3.11
- FastAPI
- PostgreSQL 15
- pgvector
- SQLAlchemy
- Pydantic
- Celery
- Redis
- sentence-transformers (local embeddings)
- Docker / Docker Compose

---

## Project Structure

```
book-recommender/
│
├── app/
│ ├── api/
│ │ ├── routes/
│ │ │ ├── uploads.py
│ │ │ └── recommend.py
│ │
│ ├── services/
│ │ ├── ingestion_service.py
│ │ ├── embedding_service.py
│ │ ├── embedding_pipeline.py
│ │ ├── embedding_provider.py
│ │ ├── recommendation_service.py
│ │ ├── normalization.py
│ │ └── upload_service.py
│ │
│ ├── repositories/
│ │ ├── book_repository.py
│ │ ├── review_repository.py
│ │ ├── upload_repository.py
│ │ ├── embedding_repository.py
│ │ ├── metrics_repository.py
│ │ └── ingestion_log_repository.py
│ │
│ ├── worker/
│ │ ├── celery_app.py
│ │ └── tasks.py
│ │
│ ├── db/
│ │ ├── session.py
│ │ ├── seed.py
│ │ └── schema.sql
│ │
│ ├── models/
│ │ └── (Pydantic models)
│ │
│ └── utils/
│   └── retry.py
│
├── data/
│ └── uploads/
│
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── README.md
```

---

## How It Works

### 1. Ingestion

- User uploads a CSV file via `/uploads`
- File is stored and a background task is triggered
- Each row is:
  - cleaned and normalized
  - validated
  - deduplicated
  - inserted into `books` and `reviews`

### 2. Embedding Pipeline

- Text is constructed from:
  - title
  - author(s)
  - review text
- Embeddings are generated using a local model:
  - `sentence-transformers/all-MiniLM-L6-v2`
- Stored in PostgreSQL (`vector(384)`)

### 3. Recommendation

- Query is embedded
- Final embedding = weighted blend
- Similar books retrieved via:

```sql
ORDER BY (b.embedding <-> :embedding)
```

### Running the Project
Prerequisites
- Docker + Docker Compose

Start services
```bash
docker-compose up --build
```

API available at
- http://localhost:8000/docs

Upload CSV
```bash
curl -X POST "http://localhost:8000/uploads" \
  -F "file=@goodreads_export.csv"
```

Get recommendations
```bash
curl -X POST "http://localhost:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "space sci-fi politics",
    "user_id": 1,
    "limit": 5
  }'
```

**Data Model (simplified)**
- books
- reviews
- uploads
- ingestion_logs
- ingestion_metrics

**Current Limitations**
- Recommendation quality is inconsistent (limited dataset + no metadata)
- No genre or external enrichment
- Ranking is naive (distance + simple rating boost)
- No evaluation or tuning framework
- No user personalization beyond basic averaging
- No production deployment setup


### Planned Improvements

**Short Term**
- Improve embedding text construction (genres, tags, metadata)
- Better ranking (hybrid scoring, weighting strategies)
- Add external data sources (e.g., Open Library, Google Books)

**Medium Term**
- Switch to OpenAI embeddings
- Add caching and batching for embedding calls
- Improve deduplication logic
- Introduce evaluation metrics for recommendation quality
- Add observability (metrics dashboard, tracing)

**Long Term**
- Full user preference modeling
- Real-time recommendations
- Scalable vector search (e.g., FAISS / external vector DB)
- Production deployment (AWS, CI/CD)
- Frontend interface
- Notes on Embeddings

Currently:
- Local model (fast, no cost)
- Lower semantic quality

Planned:
- OpenAI embeddings
- Higher semantic quality
- API cost considerations

