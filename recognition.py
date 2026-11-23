"""Qo'shiq tanish: avval Shazam (bepul), keyin AudD (ixtiyoriy)."""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

import httpx


def make_track_id(title: str, artist: str) -> str:
    raw = f"{title}|{artist}".encode("utf-8")
    return "audd:" + hashlib.sha1(raw).hexdigest()[:12]


async def _recognize_shazam(data: bytes, filename: str) -> dict | None:
    """Bepul, token talab qilmaydi."""
    if not data:
        return None
    suffix = Path(filename or "audio.ogg").suffix or ".ogg"
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / f"sample{suffix}"
        path.write_bytes(data)
        try:
            from shazamio import Shazam

            result = await Shazam().recognize(str(path))
        except Exception:
            return None
    track = (result or {}).get("track") or {}
    title = str(track.get("title") or "").strip()
    artist = str(track.get("subtitle") or "").strip()
    if not title:
        return None
    return {"title": title, "artist": artist or "Unknown"}


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
