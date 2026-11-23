"""Linkdan video/audio yuklab, Telegram'ga qaytarish."""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
from yt_dlp import YoutubeDL

from config import COOKIES_FILE, HOSTS, MAX_BYTES
from i18n import t

BASE_OPTS = {
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "socket_timeout": 20,
    "retries": 2,
}
if COOKIES_FILE:
    BASE_OPTS["cookiefile"] = COOKIES_FILE


def is_supported(url: str) -> bool:
    return any(host in url for host in HOSTS)


def _fetch(url: str, tmp: str, audio_only: bool) -> tuple[Path, dict]:
    opts = dict(BASE_OPTS)
    opts["format"] = "bestaudio/best" if audio_only else "best[ext=mp4]/best"
    opts["outtmpl"] = os.path.join(tmp, "%(id)s.%(ext)s")
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
    files = sorted(Path(tmp).glob(f"{info.get('id', '')}.*"))
    if not files:
        raise RuntimeError("Fayl topilmadi")
    return max(files, key=lambda p: p.stat().st_size), info


async def send_media(
    update: Update, context: ContextTypes.DEFAULT_TYPE, url: str, audio_only: bool, lang: str
) -> None:
    await update.effective_chat.send_action(
        ChatAction.RECORD_AUDIO if audio_only else ChatAction.UPLOAD_VIDEO
    )
    await update.message.reply_text(t("downloading", lang))
    with tempfile.TemporaryDirectory() as tmp:
        try:
            path, info = await asyncio.get_running_loop().run_in_executor(
                None, _fetch, url, tmp, audio_only
            )
            if path.stat().st_size > MAX_BYTES:
                await update.message.reply_text(t("too_large", lang))
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
            await update.message.reply_text(t("dl_error", lang, error=str(exc)[:200]))
