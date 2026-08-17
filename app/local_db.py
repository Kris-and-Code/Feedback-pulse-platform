import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "feedback.db"


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    with _connect() as conn:
        existing = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='feedback'"
        ).fetchone()
        if existing:
            columns = {row[1] for row in conn.execute("PRAGMA table_info(feedback)")}
            if "sentiment_score" in columns or columns != {
                "id",
                "review_text",
                "rating",
                "sentiment",
                "emotion",
                "created_at",
            }:
                conn.execute("DROP TABLE feedback")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                review_text TEXT NOT NULL,
                rating REAL NOT NULL,
                sentiment TEXT,
                emotion TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def store_feedback(review_text, rating, sentiment=None, emotion=None):
    init_db()
    with _connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO feedback (review_text, rating, sentiment, emotion)
            VALUES (?, ?, ?, ?)
            """,
            (review_text, rating, sentiment, emotion),
        )
        conn.commit()
        return cursor.lastrowid


def get_all_feedback():
    init_db()
    with _connect() as conn:
        cursor = conn.execute(
            "SELECT id, review_text, rating, sentiment, emotion, created_at FROM feedback ORDER BY id DESC"
        )
        columns = ["id", "review_text", "rating", "sentiment", "emotion", "created_at"]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_feedback_by_rating(rating):
    init_db()
    with _connect() as conn:
        cursor = conn.execute(
            """
            SELECT id, review_text, rating, sentiment, emotion, created_at
            FROM feedback
            WHERE rating = ?
            ORDER BY id DESC
            """,
            (rating,),
        )
        columns = ["id", "review_text", "rating", "sentiment", "emotion", "created_at"]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
