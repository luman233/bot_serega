import os
import re

API_ID = int(os.getenv("TG_API_ID", 0))
API_HASH = os.getenv("TG_API_HASH", "")
SESSION_STRING = os.getenv("TG_SESSION_STRING", "")

def parse_chat_id(x):
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

SOURCE_GROUP_IDS = [
    parse_chat_id(g)
    for g in os.getenv("SOURCE_GROUP_IDS", "").split(",")
    if g.strip()
]

# Вот так — username без @:
TARGET_GROUP_ID = "yvjyfvkkinvf"

TRIGGER_WORDS = [
    "спам",
    "реклама",
    "buy now",
    "free money",
    "example phrase",
    "тестовое слово",
]
