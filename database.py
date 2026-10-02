import sqlite3
from typing import List, Optional

DB_NAME = "jobs.db"


def init_db() -> None:
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT NOT NULL,
                source TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def save_job(title: str, company: str, location: str, source: str, url: str) -> bool:
    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                """
                INSERT INTO jobs (title, company, location, source, url)
                VALUES (?, ?, ?, ?, ?)
                """,
                (title, company, location, source, url),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def get_jobs(query: Optional[str]) -> List[dict]:
    sql = "SELECT id, title, company, location, source, url, created_at FROM jobs"
    params: List[str] = []

    if query and query.strip():
        q = f"%{query.strip()}%"
        sql += (
            " WHERE LOWER(title) LIKE LOWER(?) "
            "OR LOWER(company) LIKE LOWER(?) "
            "OR LOWER(location) LIKE LOWER(?)"
        )
        params = [q, q, q]

    sql += " ORDER BY created_at DESC"

    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, params).fetchall()

    return [dict(row) for row in rows]
