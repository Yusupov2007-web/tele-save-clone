"""@Tele_Save_Bot ga o'xshash oddiy Telegram media yuklovchi bot.

Python 3.10+  |  pip install -r requirements.txt
BOT_TOKEN=... python bot.py
"""

from __future__ import annotations

import asyncio
import os
import re
import tempfile
from pathlib import Path

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from yt_dlp import YoutubeDL

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise SystemExit("BOT_TOKEN ni o'rnating (BotFather'dan olingan token).")

URL_RE = re.compile(r"https?://[^\s<>\"']+")
HOSTS = (
    "youtube.com", "youtu.be", "tiktok.com", "instagram.com",
    "pinterest.com", "likee.com", "threads.net", "threads.com", "snapchat.com",
)
MAX_BYTES = 45 * 1024 * 1024  # Telegram yuborish chegarasi ~50 MB

BASE_OPTS = {
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "socket_timeout": 20,
    "retries": 2,
}
COOKIES = os.environ.get("COOKIES_FILE")
if COOKIES:
    BASE_OPTS["cookiefile"] = COOKIES


def _fetch(url: str, tmp: str, audio_only: bool) -> tuple[Path, dict]:
    """yt-dlp blocking ishini alohida thread'da bajarish uchun."""
    opts = dict(BASE_OPTS)
    opts["format"] = "bestaudio/best" if audio_only else "best[ext=mp4]/best"
    opts["outtmpl"] = os.path.join(tmp, "%(id)s.%(ext)s")
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
    files = sorted(Path(tmp).glob(f"{info.get('id', '')}.*"))
    if not files:
        raise RuntimeError("Fayl topilmadi (link yopiq bo'lishi mumkin).")
    return max(files, key=lambda p: p.stat().st_size), info


async def _send(update: Update, url: str, audio_only: bool) -> None:
    await update.effective_chat.send_action(
        ChatAction.RECORD_AUDIO if audio_only else ChatAction.UPLOAD_VIDEO
    )
    with tempfile.TemporaryDirectory() as tmp:
        try:
            path, info = await asyncio.get_running_loop().run_in_executor(
                None, _fetch, url, tmp, audio_only
            )
            if path.stat().st_size > MAX_BYTES:
                await update.message.reply_text("Fayl juda katta (50 MB dan oshdi).")
                return
            caption = (info.get("title") or "")[:200]
            with path.open("rb") as fh:
                if audio_only:
                    await update.message.reply_audio(audio=fh, caption=caption)
                else:
                    await update.message.reply_video(
                        video=fh, caption=caption, supports_streaming=True
                    )
        except Exception as exc:
            await update.message.reply_text(f"Yuklab bo'lmadi: {exc}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Assalomu alaykum! Ochiq video link yuboring — video yoki audioni qaytaraman.\n\n"
        "Qo'llab-quvvatlanadi: Instagram, TikTok, YouTube, Pinterest, Likee, "
        "Threads, Snapchat.\n\n"
        "/audio <link> — faqat ovozni ajratib beradi.\n"
        "/help — yordam."
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Faqat link yuboring -> video keladi.\n"
        "/audio https://... -> faqat ovoz.\n"
        "Guruhlarda ishlatish uchun BotFather orqali /setprivacy -> Disable qiling."
    )


async def audio_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = " ".join(context.args or []).strip()
    if not url:
        await update.message.reply_text("Foydalanish: /audio https://...")
        return
    await _send(update, url, audio_only=True)


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text or ""
    match = URL_RE.search(text)
    if not match:
        return
    url = match.group(0).rstrip(".,);]}")
    if not any(host in url for host in HOSTS):
        await update.message.reply_text("Bu saytni hozircha qo'llab-quvvatlamayman.")
        return
    await _send(update, url, audio_only=False)


def main() -> None:
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("audio", audio_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
