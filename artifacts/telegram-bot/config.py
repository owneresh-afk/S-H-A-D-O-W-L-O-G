import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8055441367:AAHh64lFI00rAY_MA3sVT0kcSOZs3PHQ1Ag")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "8731647972"))
DB_PATH = os.environ.get("DB_PATH", "bot_data.db")
FLASK_PORT = int(os.environ.get("PORT", "8000"))
BOT_START_TIME = None
