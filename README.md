# Tele_Save_Bot ga o'xshash bot (qayta yozilgan versiya)

@Tele_Save_Bot ning **asl kodi** ochiq emas, bu — unga o'xshash funksiyali mustaqil kod.

## Ishga tushirish

```bash
pip install -r requirements.txt
```

BotFather'dan token oling, so'ng:

```bash
# Windows PowerShell
$env:BOT_TOKEN="123456:ABC..."; python bot.py
```

Ixtiyoriy: Instagram kabi saytlar ba'zan cookie talab qiladi:

```bash
$env:COOKIES_FILE="cookies.txt"
```

## Komandalar

- Link yuboring -> video qaytadi.
- `/audio <link>` -> faqat ovoz.
- `/start`, `/help`.

Guruhlarda ishlashi uchun BotFather -> `/setprivacy` -> `Disable`.

## Qo'shish kerak bo'ladigan qismlar

- **Shazam/qo'shiq tanish**: asl botda ACRCloud yoki AudD kabi pullik API kerak (bu kodda yo'q).
- **/top, /new, /my, /settings**: chart va foydalanuvchi playlist'i uchun alohida DB (SQLite/PostgreSQL) yozish kerak.
- Faqat **ochiq** kontent yuklanadi; yopiq akkaunt va shaxsiy linklar ishlamaydi.

Eslatma: boshqa birovning videosini o'z kontentingiz sifatida tarqatish mualliflik huquqini buzishi mumkin.
