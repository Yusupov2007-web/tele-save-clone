"""Uzbek / Russian / English matnlar."""

from __future__ import annotations

LANG_NAMES = {"uz": "O'zbekcha", "ru": "Русский", "en": "English"}
REGION_NAMES = {
    "uz": "O'zbekiston", "ru": "Rossiya", "uk": "Buyuk Britaniya",
    "kz": "Qozog'iston", "tr": "Turkiya", "az": "Ozarbayjon",
}
THEME_NAMES = {"light": "☀️ Light", "dark": "🌙 Dark"}

STRINGS = {
    "uz": {
        "start": "Assalomu alaykum, {name}! 👋\nMen ijtimoiy tarmoqlardan video/audio yuklab beraman va qo'shiq tanib beraman.\n\nLink yuboring yoki tilni tanlang ↓",
        "help": "• Link yuboring → video keladi.\n• /audio <link> → faqat ovoz.\n• Ovozli xabar/audio yuboring → qo'shiq tanib beraman.\n• /top, /new → chartlar.\n• /my → saqlangan qo'shiqlar.\n• /settings → til, mintaqa, tema.\n\nGuruhlarda: BotFather → /setprivacy → Disable.",
        "choose_lang": "Tilni tanlang:",
        "saved": "✅ Saqlandi.",
        "back": "« Orqaga",
        "settings_title": "⚙️ Sozlamalar\nTil: {language}\nMintaqa: {region}\nTema: {theme}",
        "pick_lang": "Tilni tanlang:",
        "pick_region": "Mintaqani tanlang:",
        "pick_theme": "Temaning rangini tanlang:",
        "my_empty": "Hali saqlangan qo'shiq yo'q. Qo'shiq tanib ♥ bosing yoki chartlardan saqlang.",
        "my_title": "❤️ Mening ro'yxatim ({count}):",
        "top_title": "📈 {region} — eng mashhur qo'shiqlar:",
        "new_title": "🆕 {region} — yangi qo'shiqlar:",
        "charts_empty": "Chartlar hozircha bo'sh.",
        "like_added": "❤️ Ro'yxatga qo'shildi.",
        "like_removed": "🗑 Ro'yxatdan o'chirildi.",
        "recognize_wait": "🎵 Qo'shiq tanilyapti, biroz kuting...",
        "recognize_no_api": "Qo'shiq tanish o'chirilgan: AUDD_API_TOKEN o'rnatilmagan.",
        "recognize_fail": "Qo'shiq tanib bo'lmadi. Aniqroq fragment yuborib ko'ring.",
        "recognize_result": "🎶 {title} — {artist}",
        "save_button": "♥ Saqlash",
        "link_unsupported": "Bu saytni hozircha qo'llab-quvvatlamayman.",
        "downloading": "⬇️ Yuklanmoqda...",
        "too_large": "Fayl juda katta (50 MB dan oshdi).",
        "too_large_audio": "⚠️ Video juda katta, o'rniga ovoz yuboraman...",
        "dl_error": "Yuklab bo'lmadi: {error}",
        "audio_usage": "Foydalanish: /audio https://...",
    },
    "ru": {
        "start": "Здравствуйте, {name}! 👋\nЯ скачиваю видео/аудио из соцсетей и определяю песни.\n\nОтправьте ссылку или выберите язык ↓",
        "help": "• Отправьте ссылку → получите видео.\n• /audio <ссылка> → только аудио.\n• Голосовое/аудио → определю песню.\n• /top, /new → чарты.\n• /my → сохранённые песни.\n• /settings → язык, регион, тема.\n\nДля групп: BotFather → /setprivacy → Disable.",
        "choose_lang": "Выберите язык:",
        "saved": "✅ Сохранено.",
        "back": "« Назад",
        "settings_title": "⚙️ Настройки\nЯзык: {language}\nРегион: {region}\nТема: {theme}",
        "pick_lang": "Выберите язык:",
        "pick_region": "Выберите регион:",
        "pick_theme": "Выберите тему:",
        "my_empty": "Пока нет сохранённых песен. Определите песню и нажмите ♥.",
        "my_title": "❤️ Мой плейлист ({count}):",
        "top_title": "📈 {region} — популярные песни:",
        "new_title": "🆕 {region} — новые песни:",
        "charts_empty": "Чарты пока пусты.",
        "like_added": "❤️ Добавлено в плейлист.",
        "like_removed": "🗑 Удалено из плейлиста.",
        "recognize_wait": "🎵 Определяю песню, подождите...",
        "recognize_no_api": "Распознавание выключено: не задан AUDD_API_TOKEN.",
        "recognize_fail": "Не удалось определить песню. Попробуйте другой фрагмент.",
        "recognize_result": "🎶 {title} — {artist}",
        "save_button": "♥ Сохранить",
        "link_unsupported": "Этот сайт пока не поддерживается.",
        "downloading": "⬇️ Загрузка...",
        "too_large": "Файл слишком большой (более 50 МБ).",
        "too_large_audio": "⚠️ Видео слишком большое, отправляю аудио...",
        "dl_error": "Не удалось скачать: {error}",
        "audio_usage": "Использование: /audio https://...",
    },
    "en": {
        "start": "Hello, {name}! 👋\nI download videos/audio from social networks and recognize songs.\n\nSend a link or choose your language ↓",
        "help": "• Send a link → get the video.\n• /audio <link> → audio only.\n• Send a voice/audio note → I'll recognize the song.\n• /top, /new → charts.\n• /my → saved songs.\n• /settings → language, region, theme.\n\nFor groups: BotFather → /setprivacy → Disable.",
        "choose_lang": "Choose a language:",
        "saved": "✅ Saved.",
        "back": "« Back",
        "settings_title": "⚙️ Settings\nLanguage: {language}\nRegion: {region}\nTheme: {theme}",
        "pick_lang": "Choose a language:",
        "pick_region": "Choose a region:",
        "pick_theme": "Choose a theme:",
        "my_empty": "No saved songs yet. Recognize a song and tap ♥.",
        "my_title": "❤️ My playlist ({count}):",
        "top_title": "📈 {region} — top songs:",
        "new_title": "🆕 {region} — new songs:",
        "charts_empty": "Charts are empty for now.",
        "like_added": "❤️ Added to your playlist.",
        "like_removed": "🗑 Removed from your playlist.",
        "recognize_wait": "🎵 Recognizing the song, please wait...",
        "recognize_no_api": "Recognition is off: AUDD_API_TOKEN is not set.",
        "recognize_fail": "Couldn't recognize the song. Try a clearer fragment.",
        "recognize_result": "🎶 {title} — {artist}",
        "save_button": "♥ Save",
        "link_unsupported": "This site isn't supported yet.",
        "downloading": "⬇️ Downloading...",
        "too_large": "The file is too large (over 50 MB).",
        "too_large_audio": "⚠️ Video is too large, sending audio instead...",
        "dl_error": "Download failed: {error}",
        "audio_usage": "Usage: /audio https://...",
    },
}


def t(key: str, lang: str = "uz", **kwargs: object) -> str:
    text = STRINGS.get(lang, STRINGS["en"]).get(key)
    if text is None:
        text = STRINGS["en"].get(key, key)
    try:
        return text.format(**kwargs)
    except (KeyError, IndexError, ValueError):
        return text
