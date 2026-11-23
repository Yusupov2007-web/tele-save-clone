"""AudD API orqali qo'shiq tanish (ixtiyoriy, AUDD_API_TOKEN kerak)."""

from __future__ import annotations

import hashlib

import httpx


def make_track_id(title: str, artist: str) -> str:
    raw = f"{title}|{artist}".encode("utf-8")
    return "audd:" + hashlib.sha1(raw).hexdigest()[:12]


async def recognize(data: bytes, filename: str, token: str) -> dict | None:
    """Muvaffaqiyatli bo'lsa {'title','artist',...} qaytaradi, aks holda None."""
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
