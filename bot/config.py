import os
import re

API_ID = int(os.getenv("TG_API_ID", 0))
API_HASH = os.getenv("TG_API_HASH", "")
SESSION_STRING = os.getenv("TG_SESSION_STRING", "")

def parse_chat_id(x):
    """
    Преобразует строку из переменной окружения к int (если ID), к username (без @),
    либо извлекает username из ссылки вида https://t.me/username или убирает @ в начале.
    """
    x = x.strip()
    # Если ссылка на t.me
    match = re.match(r"https?://t\.me/([A-Za-z0-9_]+)", x)
    if match:
        return match.group(1)
    # Если username с @
    if x.startswith("@"):
        return x[1:]
    # Если ID
    if x.lstrip("-").isdigit():
        return int(x)
    # Просто username без @
    return x

# Список ID или username групп, которые надо мониторить
# (например, "@testejfct01,-1002803775374,https://t.me/pubgroup")
SOURCE_GROUP_IDS = [
    parse_chat_id(x) for x in os.getenv("SOURCE_GROUP_IDS", "").split(",") if x.strip()
]

# ID или username целевой группы
TARGET_GROUP_ID = parse_chat_id(os.getenv("TARGET_GROUP_ID", ""))

TRIGGER_WORDS = [
    "спам",
    "реклама",
    "тестовое слово",
    "buy now",
    "free money",
    "example phrase",
]
