# config.py

import os

# Токен вашего бота
TOKEN = "8314937843:AAFP-XP5_MtrbeY5yP1A8DH1q2vY7qmbB4o"

# Пути к JSON-файлам с текстами
LANG_KK_PATH = "data/texts_kk.json"
LANG_RU_PATH = "data/texts_ru.json"

# Путь к локальной SQLite (если нужен fallback)
DATABASE_PATH = "data/users.db"

# PostgreSQL URL (Railway) — вставьте свой DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:kErkkhRtBtYVqhdVLHrYLVNwtBDrneyw@mainline.proxy.rlwy.net:39535/railway")

# Путь к файлу с квестами
QUESTS_FILE = "data/quests.json"

QUESTS_FILE_RU = "quests_ru.json"
QUESTS_FILE_KK = "quests_kk.json"
