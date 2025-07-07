import os
import re

API_ID = int(os.getenv("TG_API_ID", 0))
API_HASH = os.getenv("TG_API_HASH", "")
SESSION_STRING = os.getenv("TG_SESSION_STRING", "")

def parse_chat_id(x):
    x = x.strip()
    if re.match(r"https?://t\.me/([A-Za-z0-9_]+)", x):
        return re.findall(r"https?://t\.me/([A-Za-z0-9_]+)", x)[0]
    if x.startswith("@"):
        return x[1:]
    if x.lstrip("-").isdigit():
        return int(x)
    return x

SOURCE_GROUP_IDS = [
    parse_chat_id(g)
    for g in os.getenv("SOURCE_GROUP_IDS", "").split(",")
    if g.strip()
]

TARGET_GROUP_ID = os.getenv("TARGET_GROUP_ID", "your_target_group")

TRIGGER_WORDS = [
    "спам",
    "реклама",
    "buy now",
    "free money",
    "example phrase",
    "тестовое слово",
]
