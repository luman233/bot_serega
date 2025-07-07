import os
import re

API_ID = int(os.getenv("TG_API_ID", 0))
API_HASH = os.getenv("TG_API_HASH", "")
SESSION_STRING = os.getenv("TG_SESSION_STRING", "")

def parse_chat_id(x):
    """
    Универсальная функция для преобразования идентификатора группы:
    - принимает Telegram id (-100...), username (с @ или без), или ссылку https://t.me/...
    - возвращает int для id, str для username
    """
    x = x.strip()
    # Если ссылка вида https://t.me/username
    match = re.match(r"https?://t\.me/([A-Za-z0-9_]+)", x)
    if match:
        return match.group(1)
    # Если username с @
    if x.startswith("@"):
        return x[1:]
    # Если числовой id
    if x.lstrip("-").isdigit():
        return int(x)
    # Просто username без @
    return x

# Список исходных групп для мониторинга (через запятую в GitHub Secrets)
SOURCE_GROUP_IDS = [
    parse_chat_id(g)
    for g in os.getenv("SOURCE_GROUP_IDS", "").split(",")
    if g.strip()
]

# Группа-получатель (id, username или ссылка), задаётся через GitHub Secrets
TARGET_GROUP_ID = parse_chat_id(os.getenv("TARGET_GROUP_ID", ""))

# Список слов/фраз для фильтрации сообщений (можно менять по необходимости)
TRIGGER_WORDS = [
    "спам",
    "реклама",
    "buy now",
    "free money",
    "example phrase",
    "тестовое слово",
]
