"""SQLite: foydalanuvchilar, saqlangan qo'shiqlar va demo chartlar."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Iterator

from config import DB_PATH


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                lang TEXT NOT NULL DEFAULT 'uz',
                region TEXT NOT NULL DEFAULT 'uz',
                theme TEXT NOT NULL DEFAULT 'light',
                username TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS tracks (
                track_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                artist TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS liked_tracks (
                user_id INTEGER NOT NULL,
                track_id TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, track_id),
                FOREIGN KEY (track_id) REFERENCES tracks(track_id)
            );
            CREATE TABLE IF NOT EXISTS charts (
                track_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                region TEXT NOT NULL,
                rank INTEGER NOT NULL,
                PRIMARY KEY (kind, region, track_id)
            );
            """
        )
    seed_charts()


def get_user(user_id: int) -> dict:
    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if row is None:
        return {"user_id": user_id, "lang": "uz", "region": "uz", "theme": "light", "username": None}
    return dict(row)


def upsert_user(user_id: int, **fields: object) -> None:
    allowed = {"lang", "region", "theme", "username"}
    data = {k: v for k, v in fields.items() if k in allowed}
    if not data:
        return
    with connect() as conn:
        conn.execute(
            """INSERT INTO users (user_id, {cols})
               VALUES (?, {q})
               ON CONFLICT(user_id) DO UPDATE SET {updates}, updated_at = CURRENT_TIMESTAMP""".format(
                cols=", ".join(data),
                q=", ".join("?" for _ in data),
                updates=", ".join(f"{k} = excluded.{k}" for k in data),
            ),
            (user_id, *data.values()),
        )


def upsert_track(track_id: str, title: str, artist: str) -> None:
    with connect() as conn:
        conn.execute(
            """INSERT INTO tracks (track_id, title, artist) VALUES (?, ?, ?)
               ON CONFLICT(track_id) DO UPDATE SET title = excluded.title, artist = excluded.artist""",
            (track_id[:60], title[:200], artist[:200]),
        )


def add_like(user_id: int, track_id: str, title: str = "", artist: str = "") -> bool:
    track_id = track_id[:60]
    with connect() as conn:
        row = conn.execute("SELECT 1 FROM tracks WHERE track_id = ?", (track_id,)).fetchone()
        if row is None:
            if not title:
                return False
            conn.execute(
                "INSERT INTO tracks (track_id, title, artist) VALUES (?, ?, ?)",
                (track_id, title[:200], artist[:200]),
            )
        cur = conn.execute(
            "INSERT OR IGNORE INTO liked_tracks (user_id, track_id) VALUES (?, ?)",
            (user_id, track_id),
        )
        return cur.rowcount > 0


def remove_like(user_id: int, track_id: str) -> None:
    with connect() as conn:
        conn.execute(
            "DELETE FROM liked_tracks WHERE user_id = ? AND track_id = ?",
            (user_id, track_id[:60]),
        )


def list_likes(user_id: int) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            """SELECT t.track_id, t.title, t.artist FROM liked_tracks l
               JOIN tracks t ON t.track_id = l.track_id
               WHERE l.user_id = ? ORDER BY l.created_at DESC""",
            (user_id,),
        ).fetchall()
    return [dict(r) for r in rows]


DEMO_ARTISTS = ("Demo Artist", "Studio One", "New Sound", "Melody Lab", "Night Radio")


def seed_charts() -> None:
    """Demo ma'lumotlar — keyincha real chart API bilan almashtirish mumkin."""
    with connect() as conn:
        if conn.execute("SELECT 1 FROM charts LIMIT 1").fetchone():
            return
        for region in ("uz", "ru", "uk", "kz", "tr", "az"):
            for kind in ("top", "new"):
                for i in range(1, 6):
                    track_id = f"demo-{region}-{kind}-{i}"
                    title = f"{region.upper()} {kind.title()} Hit {i}"
                    artist = DEMO_ARTISTS[(i - 1) % len(DEMO_ARTISTS)]
                    conn.execute(
                        "INSERT OR IGNORE INTO tracks (track_id, title, artist) VALUES (?, ?, ?)",
                        (track_id, title, artist),
                    )
                    conn.execute(
                        "INSERT OR IGNORE INTO charts (track_id, kind, region, rank) VALUES (?, ?, ?, ?)",
                        (track_id, kind, region, i),
                    )


def get_charts(kind: str, region: str, limit: int = 10) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            """SELECT c.track_id, t.title, t.artist FROM charts c
               JOIN tracks t ON t.track_id = c.track_id
               WHERE c.kind = ? AND c.region = ? ORDER BY c.rank LIMIT ?""",
            (kind, region, limit),
        ).fetchall()
    return [dict(r) for r in rows]
