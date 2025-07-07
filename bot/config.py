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
    match = re.match(r"https?://t\.me/([A-Za-z0-9_]+)", x)
    if match:
        return match.group(1)
    if x.startswith("@"):
        return x[1:]
    if x.lstrip("-").isdigit():
        return int(x)
    return x

SOURCE_GROUP_IDS = [
    parse_chat_id(x) for x in os.getenv("SOURCE_GROUP_IDS", "").split(",") if x.strip()
]

TARGET_GROUP_ID = parse_chat_id(os.getenv("TARGET_GROUP_ID", ""))

TRIGGER_WORDS = [
    "спам",
    "реклама",
    "тестовое слово",
    "buy now",
    "free money",
    "example phrase",
]
