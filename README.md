# tele-save-clone

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![python-telegram-bot](https://img.shields.io/badge/PTB-21%2B-2CA5E0)](https://python-telegram-bot.readthedocs.io/)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-latest-orange)](https://github.com/yt-dlp/yt-dlp)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[@Tele_Save_Bot](https://t.me/Tele_Save_Bot) ga o'xshash, noldan yozilgan Telegram bot. Asl botning kodi ochiq emas — bu mustaqil qayta yozilgan versiya.

## Imkoniyatlar

- 📥 Link yuboring → Instagram, TikTok, YouTube, Pinterest, Likee, Threads, Snapchat videolarini yuklab beradi.
- 🎧 `/audio <link>` → faqat ovozni ajratadi.
- 📺 `/hd <link>` → to'liq sifat (sekinroq bo'lishi mumkin).
- 🎵 Ovozli xabar/audio/video yuboring → **qo'shiq tanib beradi** (AudD API bilan).
- 📈 `/top`, `/new` → mintaqa bo'yicha chartlar (demo ma'lumotlar).
- ❤️ `/my` → saqlangan qo'shiqlar ro'yxati, like/unlike tugmalari.
- ⚙️ `/settings` → til (uz / ru / en), mintaqa, tema.
- 👥 Guruhlarda ishlaydi (BotFather orqali privacy o'chiriladi).

## Tez boshlash

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

`.env.example` ni `.env` ga nusxalab, `BOT_TOKEN` ni to'ldiring. Keyin:

```powershell
$env:BOT_TOKEN="123456:ABC..."
python bot.py
```

Yoki `.env` ni avtomatik o'qish uchun `pip install python-dotenv` qo'shib, `bot.py` boshiga `from dotenv import load_dotenv; load_dotenv()` yozing.

### Muhit o'zgaruvchilari

| O'zgaruvchi | Majburiy | Tavsif |
|---|---|---|
| `BOT_TOKEN` | ✅ | BotFather'dan olingan token |
| `COOKIES_FILE` | ❌ | Yopiqroq saytlar uchun `cookies.txt` yo'li |
| `AUDD_API_TOKEN` | ❌ | Qo'shiq tanish uchun [AudD](https://audd.io) tokeni |
| `DB_PATH` | ❌ | SQLite fayli (default: `bot_data.sqlite3`) |

## Komandalar

| Komanda | Vazifa |
|---|---|
| `/start` | Boshlash va til tanlash |
| `/help` | Yordam |
| `/audio <link>` | Faqat audio |
| `/top` / `/new` | Chartlar |
| `/my` | Saqlangan qo'shiqlar |
| `/settings` | Til, mintaqa, tema |

## Tuzilma

```
bot.py           # handlerlar va tugmalar
config.py        # sozlamalar
db.py            # SQLite: user, like, chart
downloader.py    # yt-dlp yuklash
recognition.py   # AudD qo'shiq tanish
i18n.py          # uz / ru / en matnlar
requirements.txt
```

## Eslatmalar

- Faqat **ochiq** kontent yuklanadi; shaxsiy akkaunt va linklar ishlamaydi.
- Chartlar hozircha **demo** ma'lumotlar (`db.py` ichidagi `seed_charts()`) — real API bilan almashtirish mumkin.
- AudD tokensiz qo'shiq tanish o'chirib qo'yiladi (bot ishlayveradi).
- Boshqa birovning videosini o'z kontentingiz sifatida tarqatish mualliflik huquqini buzishi mumkin.
