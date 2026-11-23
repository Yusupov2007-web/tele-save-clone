"""Sozlamalar va konstantalar (faqat muhit o'zgaruvchilaridan o'qiladi)."""

from __future__ import annotations

import os

TOKEN = os.environ.get("BOT_TOKEN", "")
COOKIES_FILE = os.environ.get("COOKIES_FILE")
AUDD_TOKEN = os.environ.get("AUDD_API_TOKEN", "")
DB_PATH = os.environ.get("DB_PATH", "bot_data.sqlite3")

MAX_BYTES = 45 * 1024 * 1024  # Telegram yuborish chegarasi ~50 MB

HOSTS = (
    "youtube.com", "youtu.be", "tiktok.com", "instagram.com",
    "pinterest.com", "likee.com", "threads.net", "threads.com", "snapchat.com",
)

LANGS = ("uz", "ru", "en")
REGIONS = ("uz", "ru", "uk", "kz", "tr", "az")
THEMES = ("light", "dark")
