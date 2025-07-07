import os

# Телеграм API ID и HASH — брать с https://my.telegram.org
API_ID = int(os.getenv("TG_API_ID", 0))
API_HASH = os.getenv("TG_API_HASH", "")
# Строка сессии userbot (Pyrogram StringSession)
SESSION_STRING = os.getenv("TG_SESSION_STRING", "")

def parse_chat_id(x):
    x = x.strip()
    if x.lstrip("-").isdigit():
        return int(x)
    return x

# Список ID групп, которые надо мониторить (группа-источник)
SOURCE_GROUP_IDS = [
    -1002803775374
]

# ID целевой группы (куда будут пересылаться сообщения)
TARGET_GROUP_ID = -1002467611553

# Список слов/фраз для фильтрации (чувствительность к регистру отключена)
TRIGGER_WORDS = [
    "спам",
    "реклама",
    "тестовое слово",
    "buy now",
    "free money",
    "example phrase",
]
