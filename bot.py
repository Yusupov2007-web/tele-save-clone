"""Telegram media bot — asosiy kirish nuqtasi."""

from __future__ import annotations

import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import db
from config import AUDD_TOKEN, LANGS, REGIONS, THEMES, TOKEN
from downloader import is_supported, send_media
from i18n import LANG_NAMES, REGION_NAMES, THEME_NAMES, t
from recognition import make_track_id, recognize

URL_RE = re.compile(r"https?://[^\s<>\"']+")
MAPPINGS = {"lang": LANG_NAMES, "region": REGION_NAMES, "theme": THEME_NAMES}
VALID = {"lang": LANGS, "region": REGIONS, "theme": THEMES}


def _label(mapping: dict, key: str) -> str:
    return mapping.get(key, key)


def lang_kb(lang: str, kind: str) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(label, callback_data=f"set:{kind}:{value}")
        for value, label in MAPPINGS[kind].items()
    ]
    rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    rows.append([InlineKeyboardButton(t("back", lang), callback_data="settings:back")])
    return InlineKeyboardMarkup(rows)


def settings_text(user: dict) -> str:
    lang = user["lang"]
    return t(
        "settings_title",
        lang,
        language=_label(LANG_NAMES, lang),
        region=_label(REGION_NAMES, user["region"]),
        theme=_label(THEME_NAMES, user["theme"]),
    )


def settings_kb(user: dict) -> InlineKeyboardMarkup:
    lang = user["lang"]
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(f"🌐 {_label(LANG_NAMES, lang)}", callback_data="pick:lang")],
            [
                InlineKeyboardButton(
                    f"📍 {_label(REGION_NAMES, user['region'])}", callback_data="pick:region"
                )
            ],
            [
                InlineKeyboardButton(
                    f"🎨 {_label(THEME_NAMES, user['theme'])}", callback_data="pick:theme"
                )
            ],
        ]
    )


def my_content(user: dict) -> tuple[str, InlineKeyboardMarkup | None]:
    lang = user["lang"]
    likes = db.list_likes(user["user_id"])
    if not likes:
        return t("my_empty", lang), None
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"🗑 {row['title']} — {row['artist']}",
                    callback_data=f"unlike:{row['track_id']}",
                )
            ]
            for row in likes
        ]
    )
    return t("my_title", lang, count=len(likes)), keyboard


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_tg = update.effective_user
    db.upsert_user(user_tg.id, username=user_tg.username or "")
    user = db.get_user(user_tg.id)
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(name, callback_data=f"set:lang:{code}") for code, name in LANG_NAMES.items()]]
    )
    name = user_tg.first_name or user_tg.username or "do'stim"
    await update.message.reply_text(
        t("start", user["lang"], name=name), reply_markup=keyboard
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = db.get_user(update.effective_user.id)
    await update.message.reply_text(t("help", user["lang"]))


async def hd_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = db.get_user(update.effective_user.id)
    url = " ".join(context.args or "").strip()
    if not url:
        await update.message.reply_text("Foydalanish: /hd https://...")
        return
    await send_media(update, context, url, audio_only=False, lang=user["lang"], max_height=0)


async def settings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = db.get_user(update.effective_user.id)
    await update.message.reply_text(
        settings_text(user), reply_markup=settings_kb(user)
    )


async def charts_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, kind: str) -> None:
    user = db.get_user(update.effective_user.id)
    lang = user["lang"]
    region = _label(REGION_NAMES, user["region"])
    rows = db.get_charts(kind, user["region"])
    text = t(f"{kind}_title", lang, region=region)
    if not rows:
        await update.message.reply_text(text + "\n" + t("charts_empty", lang))
        return
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"♥ {row['title']} — {row['artist']}",
                    callback_data=f"like:{row['track_id']}",
                )
            ]
            for row in rows
        ]
    )
    await update.message.reply_text(text, reply_markup=keyboard)


async def top_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await charts_cmd(update, context, "top")


async def new_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await charts_cmd(update, context, "new")


async def my_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text, keyboard = my_content(db.get_user(update.effective_user.id))
    await update.message.reply_text(text, reply_markup=keyboard)


async def audio_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = db.get_user(update.effective_user.id)
    url = " ".join(context.args or []).strip()
    if not url:
        await update.message.reply_text(t("audio_usage", user["lang"]))
        return
    await send_media(update, context, url, audio_only=True, lang=user["lang"])


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = db.get_user(update.effective_user.id)
    match = URL_RE.search(update.message.text or "")
    if not match:
        return
    url = match.group(0).rstrip(".,);]}")
    if not is_supported(url):
        await update.message.reply_text(t("link_unsupported", user["lang"]))
        return
    await send_media(update, context, url, audio_only=False, lang=user["lang"])


async def on_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = db.get_user(update.effective_user.id)
    lang = user["lang"]
    if not AUDD_TOKEN:
        await update.message.reply_text(t("recognize_no_api", lang))
        return
    message = update.message
    media = message.voice or message.audio or message.video or message.video_note
    if media is None:
        return
    await message.reply_text(t("recognize_wait", lang))
    try:
        file = await media.get_file()
        raw = await file.download_as_bytearray()
        filename = getattr(media, "file_name", None) or "audio.ogg"
        result = await recognize(bytes(raw), filename, AUDD_TOKEN)
    except Exception:
        result = None
    if not result:
        await message.reply_text(t("recognize_fail", lang))
        return
    title, artist = result["title"], result["artist"]
    track_id = make_track_id(title, artist)
    db.upsert_track(track_id, title, artist)
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(t("save_button", lang), callback_data=f"save:{track_id}")]]
    )
    await message.reply_text(
        t("recognize_result", lang, title=title, artist=artist), reply_markup=keyboard
    )


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data or ""
    uid = query.from_user.id
    user = db.get_user(uid)
    lang = user["lang"]

    if data.startswith("set:"):
        _, kind, value = data.split(":", 2)
        if kind in VALID and value in VALID[kind]:
            db.upsert_user(uid, **{kind: value})
            user = db.get_user(uid)
            await query.edit_message_text(
                t("saved", user["lang"]), reply_markup=settings_kb(user)
            )
        return

    if data.startswith("pick:"):
        kind = data.split(":", 1)[1]
        if kind in MAPPINGS:
            await query.edit_message_text(
                t(f"pick_{kind}", lang), reply_markup=lang_kb(lang, kind)
            )
        return

    if data == "settings:back":
        user = db.get_user(uid)
        await query.edit_message_text(
            settings_text(user), reply_markup=settings_kb(user)
        )
        return

    if data.startswith(("like:", "save:")):
        track_id = data.split(":", 1)[1]
        added = db.add_like(uid, track_id)
        await query.answer(t("like_added" if added else "like_removed", lang))
        return

    if data.startswith("unlike:"):
        db.remove_like(uid, data.split(":", 1)[1])
        user = db.get_user(uid)
        text, keyboard = my_content(user)
        await query.edit_message_text(text, reply_markup=keyboard)
        return


def main() -> None:
    if not TOKEN:
        raise SystemExit("BOT_TOKEN ni o'rnating (.env.example ga qarang).")
    db.init_db()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("settings", settings_cmd))
    app.add_handler(CommandHandler("top", top_cmd))
    app.add_handler(CommandHandler("new", new_cmd))
    app.add_handler(CommandHandler("my", my_cmd))
    app.add_handler(CommandHandler("audio", audio_cmd))
    app.add_handler(CommandHandler("hd", hd_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(
        MessageHandler(filters.VOICE | filters.AUDIO | filters.VIDEO | filters.VIDEO_NOTE, on_media)
    )
    app.add_handler(CallbackQueryHandler(on_callback))
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
