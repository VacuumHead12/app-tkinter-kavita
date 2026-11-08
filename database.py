"""
Database module for KAVITA Movie Recommendation System.
Provides persistent storage using SQLite for watchlist, watched movies,
favourites, user ratings/reviews, and poster path cache.
"""

import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "kavita.db")


def get_connection():
    """Returns a SQLite connection with Row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the database schema and creates necessary tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Watchlist table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            movie_id INTEGER PRIMARY KEY,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Watched movies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watched (
            movie_id INTEGER PRIMARY KEY,
            watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Favourites table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favourites (
            movie_id INTEGER PRIMARY KEY,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # User reviews and ratings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            movie_id INTEGER PRIMARY KEY,
            rating REAL,
            review_text TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Poster cache table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS poster_cache (
            movie_id INTEGER PRIMARY KEY,
            poster_path TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    # Pre-populate poster_cache if poster_paths_cache.json exists
    cache_file = os.path.join(os.path.dirname(__file__), "poster_paths_cache.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                cached = json.load(f)
                for mid_str, path in cached.items():
                    cursor.execute("""
                        INSERT OR IGNORE INTO poster_cache (movie_id, poster_path)
                        VALUES (?, ?)
                    """, (int(mid_str), path))
            conn.commit()
        except Exception:
            pass

    conn.close()


# ==================== WATCHLIST ====================

def add_to_watchlist(movie_id: int):
    conn = get_connection()
    with conn:
        conn.execute("INSERT OR IGNORE INTO watchlist (movie_id) VALUES (?)", (movie_id,))
    conn.close()


def remove_from_watchlist(movie_id: int):
    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM watchlist WHERE movie_id = ?", (movie_id,))
    conn.close()


def is_in_watchlist(movie_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM watchlist WHERE movie_id = ?", (movie_id,))
    res = cursor.fetchone() is not None
    conn.close()
    return res


def get_watchlist() -> list[int]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT movie_id FROM watchlist ORDER BY added_at DESC")
    rows = [row["movie_id"] for row in cursor.fetchall()]
    conn.close()
    return rows


# ==================== WATCHED ====================

def add_to_watched(movie_id: int):
    conn = get_connection()
    with conn:
        conn.execute("INSERT OR IGNORE INTO watched (movie_id) VALUES (?)", (movie_id,))
    conn.close()


def remove_from_watched(movie_id: int):
    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM watched WHERE movie_id = ?", (movie_id,))
    conn.close()


def is_watched(movie_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM watched WHERE movie_id = ?", (movie_id,))
    res = cursor.fetchone() is not None
    conn.close()
    return res


def get_watched() -> list[int]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT movie_id FROM watched ORDER BY watched_at DESC")
    rows = [row["movie_id"] for row in cursor.fetchall()]
    conn.close()
    return rows


# ==================== FAVOURITES ====================

def add_to_favourites(movie_id: int):
    conn = get_connection()
    with conn:
        conn.execute("INSERT OR IGNORE INTO favourites (movie_id) VALUES (?)", (movie_id,))
    conn.close()


def remove_from_favourites(movie_id: int):
    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM favourites WHERE movie_id = ?", (movie_id,))
    conn.close()


def is_favourite(movie_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM favourites WHERE movie_id = ?", (movie_id,))
    res = cursor.fetchone() is not None
    conn.close()
    return res


def get_favourites() -> list[int]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT movie_id FROM favourites ORDER BY added_at DESC")
    rows = [row["movie_id"] for row in cursor.fetchall()]
    conn.close()
    return rows


# ==================== REVIEWS & RATINGS ====================

def save_review(movie_id: int, rating: float, review_text: str):
    conn = get_connection()
    with conn:
        conn.execute("""
            INSERT INTO reviews (movie_id, rating, review_text, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(movie_id) DO UPDATE SET
                rating = excluded.rating,
                review_text = excluded.review_text,
                updated_at = CURRENT_TIMESTAMP
        """, (movie_id, rating, review_text.strip()))
    conn.close()


def get_review(movie_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT movie_id, rating, review_text, updated_at FROM reviews WHERE movie_id = ?", (movie_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "movie_id": row["movie_id"],
            "rating": row["rating"],
            "review_text": row["review_text"],
            "updated_at": row["updated_at"]
        }
    return None


def get_all_reviews() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT movie_id, rating, review_text, updated_at FROM reviews ORDER BY updated_at DESC")
    rows = [
        {
            "movie_id": row["movie_id"],
            "rating": row["rating"],
            "review_text": row["review_text"],
            "updated_at": row["updated_at"]
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return rows


def delete_review(movie_id: int):
    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM reviews WHERE movie_id = ?", (movie_id,))
    conn.close()


# ==================== USER STATS ====================

def get_user_stats() -> dict:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM watched")
    watched_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM watchlist")
    watchlist_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM favourites")
    favourites_count = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count, AVG(rating) as avg_rating FROM reviews")
    rev_row = cursor.fetchone()
    review_count = rev_row["count"] or 0
    avg_rating = rev_row["avg_rating"] or 0.0

    conn.close()

    return {
        "watched_count": watched_count,
        "watchlist_count": watchlist_count,
        "favourites_count": favourites_count,
        "review_count": review_count,
        "average_rating": round(avg_rating, 1)
    }


# ==================== POSTER CACHE ====================

def cache_poster_path(movie_id: int, poster_path: str):
    conn = get_connection()
    with conn:
        conn.execute("""
            INSERT OR REPLACE INTO poster_cache (movie_id, poster_path, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (movie_id, poster_path))
    conn.close()


def get_cached_poster_path(movie_id: int) -> str | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT poster_path FROM poster_cache WHERE movie_id = ?", (movie_id,))
    row = cursor.fetchone()
    conn.close()
    return row["poster_path"] if row else None


# Initialize on module import
init_db()
