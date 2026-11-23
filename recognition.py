"""Qo'shiq tanish: avval Shazam (bepul), keyin AudD (ixtiyoriy)."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import tempfile
from pathlib import Path

import httpx


def make_track_id(title: str, artist: str) -> str:
    raw = f"{title}|{artist}".encode("utf-8")
    return "audd:" + hashlib.sha1(raw).hexdigest()[:12]


def _to_wav(data: bytes, filename: str, tmp: str) -> Path | None:
    """Telegram ovozli xabarlarini Shazam yaxshi tanishi uchun WAV ga aylantiradi."""
    if not shutil.which("ffmpeg"):
        return None
    src = Path(tmp) / (Path(filename or "audio").name or "audio.ogg")
    src.write_bytes(data)
    dst = Path(tmp) / "sample.wav"
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-i", str(src),
                "-t", "20", "-ar", "16000", "-ac", "1",
                str(dst),
            ],
            check=True,
            capture_output=True,
            timeout=30,
        )
    except Exception:
        return None
    return dst if dst.exists() and dst.stat().st_size > 0 else None


async def _recognize_shazam(data: bytes, filename: str) -> dict | None:
    """Bepul, token talab qilmaydi."""
    if not data:
        return None
    with tempfile.TemporaryDirectory() as tmp:
        wav = _to_wav(data, filename, tmp)
        candidates: list[str] = []
        if wav is not None:
            candidates.append(str(wav))
        orig = Path(tmp) / (Path(filename or "audio.ogg").name or "audio.ogg")
        if not orig.exists():
            orig.write_bytes(data)
        candidates.append(str(orig))

        try:
            from shazamio import Shazam

            shazam = Shazam()
        except Exception:
            return None

        for path in candidates:
            try:
                result = await shazam.recognize(path)
            except Exception:
                continue
            track = (result or {}).get("track") or {}
            title = str(track.get("title") or "").strip()
            artist = str(track.get("subtitle") or "").strip()
            if title:
                return {"title": title, "artist": artist or "Unknown"}
    return None


async def _recognize_audd(data: bytes, filename: str, token: str) -> dict | None:
    if not token or not data:
        return None
    try:
        async with httpx.AsyncClient(timeout=40) as client:
            response = await client.post(
                "https://api.audd.io/",
                data={"api_token": token, "return": "title,artist"},
                files={"file": (filename or "audio.ogg", data)},
            )
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError):
        return None
    if payload.get("status") != "success":
        return None
    result = payload.get("result")
    if not isinstance(result, dict):
        return None
    title = str(result.get("title") or "").strip()
    artist = str(result.get("artist") or "").strip()
    if not title:
        return None
    return {"title": title, "artist": artist or "Unknown"}


async def recognize(data: bytes, filename: str, token: str = "") -> dict | None:
    """Avval Shazam, topilmasa AudD. {'title','artist'} yoki None."""
    result = await _recognize_shazam(data, filename)
    if result:
        return result
    return await _recognize_audd(data, filename, token)
