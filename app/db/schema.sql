-- USERS
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- UPLOADS
CREATE TABLE IF NOT EXISTS uploads (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),

    filename TEXT NOT NULL,
    file_path TEXT,

    status TEXT DEFAULT 'pending',  -- pending | processing | completed | failed
    error_message TEXT,

    last_processed_row INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- vector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- BOOKS
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    goodreads_book_id TEXT,
    title TEXT NOT NULL,
    author TEXT,
    additional_authors TEXT,

    normalized_title TEXT,
    normalized_author TEXT,

    embedding vector(384),

    created_at TIMESTAMP DEFAULT NOW()
);

-- Unique constraint
CREATE UNIQUE INDEX IF NOT EXISTS unique_books_normalized
ON books (normalized_title, normalized_author);

CREATE UNIQUE INDEX unique_books_with_author
ON books (normalized_title, normalized_author)
WHERE normalized_author IS NOT NULL;

CREATE UNIQUE INDEX unique_books_without_author
ON books (normalized_title)
WHERE normalized_author IS NULL;

-- REVIEWS
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,

    user_id INTEGER REFERENCES users(id),
    book_id INTEGER REFERENCES books(id),
    upload_id INTEGER REFERENCES uploads(id),

    rating INTEGER,
    review_text TEXT,
    date_read DATE,
    --embedding vector(1536), -- for openai provider later
    embedding vector(384),

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE (user_id, book_id)
);

-- INGESTION_LOGS
CREATE TABLE IF NOT EXISTS ingestion_logs (
    id SERIAL PRIMARY KEY,
    upload_id INTEGER REFERENCES uploads(id),
    step TEXT,
    message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- INGESTION_METRICS
CREATE TABLE IF NOT EXISTS ingestion_metrics (
    id SERIAL PRIMARY KEY,
    upload_id INTEGER REFERENCES uploads(id),

    total_rows INTEGER,
    processed_rows INTEGER,
    skipped_unread INTEGER,
    skipped_invalid INTEGER,

    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
