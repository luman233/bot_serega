import os

# Телеграм API ID и HASH — брать с https://my.telegram.org
API_ID = int(os.getenv("TG_API_ID", 0))
API_HASH = os.getenv("TG_API_HASH", "")
# Строка сессии userbot (Pyrogram StringSession)
SESSION_STRING = os.getenv("TG_SESSION_STRING", "")

# Список ID групп, которые надо мониторить (обязательно указывать со знаком минус! Пример: -1001234567890)
SOURCE_GROUP_IDS = [
    int(x) for x in os.getenv("SOURCE_GROUP_IDS", "-1002803775374").split(",")
]

# ID целевой группы (куда будут пересылаться сообщения)
TARGET_GROUP_ID = int(os.getenv("TARGET_GROUP_ID", 0))

# Список слов/фраз для фильтрации (чувствительность к регистру отключена)
TRIGGER_WORDS = [
    "спам",
    "реклама",
    "тестовое слово",
    "buy now",
    "free money",
    "example phrase",
]
