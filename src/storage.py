"""SQLite storage for tweets and summaries."""

import sqlite3
import json
import os
from datetime import datetime

from src.config import DATA_DIR

DB_PATH = os.path.join(DATA_DIR, "data.db")


def _get_db() -> sqlite3.Connection:
    """Get a database connection, creating tables if needed."""
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("""
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            summary TEXT NOT NULL,
            tweet_count INTEGER NOT NULL,
            hours INTEGER NOT NULL,
            tweets_json TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    db.execute("CREATE INDEX IF NOT EXISTS idx_summaries_username ON summaries(username)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_summaries_created ON summaries(created_at)")
    db.commit()
    return db


def save_summary(username: str, summary: str, tweets: list[dict], hours: int):
    """Save a summary and its source tweets to the database."""
    db = _get_db()
    db.execute(
        "INSERT INTO summaries (username, summary, tweet_count, hours, tweets_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (username, summary, len(tweets), hours, json.dumps(tweets, ensure_ascii=False), datetime.now().isoformat()),
    )
    db.commit()
    db.close()


def get_history(limit: int = 50, search: str = "") -> list[dict]:
    """Retrieve summary history, optionally filtered by search term."""
    db = _get_db()
    if search:
        rows = db.execute(
            "SELECT * FROM summaries WHERE username LIKE ? OR summary LIKE ? ORDER BY created_at DESC LIMIT ?",
            (f"%{search}%", f"%{search}%", limit),
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM summaries ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    db.close()
    return [dict(r) for r in rows]
