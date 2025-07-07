import os

# Телеграм API ID и HASH — брать с https://my.telegram.org
API_ID = int(os.getenv("TG_API_ID", 0))
API_HASH = os.getenv("TG_API_HASH", "")
# Строка сессии userbot (Pyrogram StringSession)
SESSION_STRING = os.getenv("TG_SESSION_STRING", "")

def parse_chat_id(x):
    """Возвращает int для числовых id и str для username (без @)"""
    x = x.strip()
    if x.lstrip("-").isdigit():
        return int(x)
    return x

# Список ID групп или username групп (без @), которые надо мониторить
# Пример для переменной окружения: "testejfct01,-1001234567890"
SOURCE_GROUP_IDS = [
    parse_chat_id(x) for x in os.getenv("SOURCE_GROUP_IDS", "testejfct01").split(",")
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
