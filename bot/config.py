import os

API_ID = int(os.getenv("TG_API_ID", 0))
API_HASH = os.getenv("TG_API_HASH", "")
SESSION_STRING = os.getenv("TG_SESSION_STRING", "")

# ID целевой группы, куда будут пересылаться сообщения с триггер-словами
TARGET_GROUP_ID = int(os.getenv("TARGET_GROUP_ID", 0))

# Список слов/фраз для отслеживания (можно редактировать)
TRIGGER_WORDS = [
    "спам",
    "реклама",
    "тестовое слово",
    "buy now",
    "free money",
    "example phrase",
]
