import os
from sqlalchemy import create_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@db:5432/books"
)

def run_schema():
    engine = create_engine(DATABASE_URL)

    with open("app/db/schema.sql", "r") as f:
        sql = f.read()

    with engine.begin() as conn:
        conn.exec_driver_sql(sql)

        conn.exec_driver_sql("""
            INSERT INTO users (email)
            VALUES ('test@example.com')
            ON CONFLICT DO NOTHING;
        """)


if __name__ == "__main__":
    run_schema()

    print("Database schema initialized.")
