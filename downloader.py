"""Linkdan video/audio yuklab, Telegram'ga qaytarish."""

from __future__ import annotations

import asyncio
import os
import shutil
import tempfile
from pathlib import Path

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
from yt_dlp import YoutubeDL

from config import COOKIES_FILE, HOSTS, MAX_BYTES, MAX_HEIGHT
from i18n import t

BASE_OPTS = {
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "socket_timeout": 30,
    "retries": 2,
    "fragment_retries": 3,
    "concurrent_fragment_downloads": 8,
    "http_chunk_size": 1024 * 1024,
}
if COOKIES_FILE:
    BASE_OPTS["cookiefile"] = COOKIES_FILE
if shutil.which("aria2c"):
    BASE_OPTS["external_downloader"] = "aria2c"
    BASE_OPTS["external_downloader_args"] = {"aria2c": ["-x", "8", "-s", "8", "-k", "1M"]}


def is_supported(url: str) -> bool:
    return any(host in url for host in HOSTS)


def _video_format(max_height: int) -> str:
    if max_height <= 0:
        return "best[ext=mp4]/best"
    return (
        f"bestvideo[ext=mp4][height<={max_height}]+bestaudio[ext=m4a]/"
        f"best[ext=mp4][height<={max_height}]/best[ext=mp4]/best"
    )


def _fetch(url: str, tmp: str, audio_only: bool, max_height: int) -> tuple[Path, dict]:
    opts = dict(BASE_OPTS)
    opts["format"] = "bestaudio/best" if audio_only else _video_format(max_height)
    opts["merge_output_format"] = "mp4"
    opts["outtmpl"] = os.path.join(tmp, "%(id)s.%(ext)s")
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
    files = sorted(Path(tmp).glob(f"{info.get('id', '')}.*"))
    if not files:
        raise RuntimeError("Fayl topilmadi")
    return max(files, key=lambda p: p.stat().st_size), info


async def send_media(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    url: str,
    audio_only: bool,
    lang: str,
    max_height: int = MAX_HEIGHT,
) -> None:
    await update.effective_chat.send_action(
        ChatAction.RECORD_AUDIO if audio_only else ChatAction.UPLOAD_VIDEO
    )
    await update.message.reply_text(t("downloading", lang))
    with tempfile.TemporaryDirectory() as tmp:
        try:
            path, info = await asyncio.get_running_loop().run_in_executor(
                None, _fetch, url, tmp, audio_only, max_height
            )
            if path.stat().st_size > MAX_BYTES and not audio_only:
                path, info = await asyncio.get_running_loop().run_in_executor(
                    None, _fetch, url, tmp, True, max_height
                )
                audio_only = True
                await update.message.reply_text(t("too_large_audio", lang))
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
