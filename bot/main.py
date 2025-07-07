import asyncio
import hashlib
from pyrogram import Client
from config import API_ID, API_HASH, SESSION_STRING, SOURCE_GROUP_IDS, TARGET_GROUP_ID, TRIGGER_WORDS
from datetime import datetime, timedelta, timezone
import os
from pyrogram.types import Message

PERIOD_MINUTES = 10
HASH_TTL_DAYS = 7

BASE_DIR = os.path.dirname(__file__)
HASH_DIR = os.path.join(BASE_DIR, "hashes")

app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

def is_trigger(text):
    return any(word.lower() in text.lower() for word in TRIGGER_WORDS)

def ensure_hash_dir(group_id):
    path = os.path.join(HASH_DIR, str(group_id).replace("@", "").replace("-", "m"))
    os.makedirs(path, exist_ok=True)
    return path

def hash_message(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def hash_file_path(group_id, hash_str):
    group_dir = ensure_hash_dir(group_id)
    return os.path.join(group_dir, f"{hash_str}.txt")

def is_hash_known(group_id, hash_str):
    return os.path.exists(hash_file_path(group_id, hash_str))

def save_hash(group_id, hash_str):
    path = hash_file_path(group_id, hash_str)
    with open(path, "w") as f:
        f.write(datetime.now(timezone.utc).isoformat())
    print(f"💾 Сохранили хеш {hash_str[:8]} для группы {group_id}")

def clean_old_hashes(group_id):
    group_dir = ensure_hash_dir(group_id)
    cutoff = datetime.now(timezone.utc) - timedelta(days=HASH_TTL_DAYS)
    for fname in os.listdir(group_dir):
        fpath = os.path.join(group_dir, fname)
        try:
            with open(fpath, "r") as f:
                ts = datetime.fromisoformat(f.read().strip())
            if ts < cutoff:
                os.remove(fpath)
        except Exception:
            os.remove(fpath)

def format_forwarded_message(msg):
    text = msg.text or ""
    text += "\n\n"
    if msg.chat.username:
        chat_link = f"https://t.me/{msg.chat.username}"
    elif str(msg.chat.id).startswith("-100"):
        chat_link = f"https://t.me/c/{str(msg.chat.id)[4:]}"
    else:
        chat_link = str(msg.chat.id)
    text += chat_link + "\n"
    text += (msg.chat.title or str(msg.chat.id)) + "\n"
    if msg.from_user and msg.from_user.username:
        text += f"@{msg.from_user.username}"
    elif msg.from_user:
        text += f"ID: {msg.from_user.id}"
    else:
        text += "Без имени"
    return text

async def process_group(client, group_id, after_ts):
    print(f"\n🔍 Обработка группы: {group_id}")
    clean_old_hashes(group_id)

    async for msg in client.get_chat_history(group_id, limit=100):
        if not isinstance(msg, Message) or not msg.text or not isinstance(msg.id, int):
            continue
        if msg.from_user and msg.from_user.is_self:
            continue

        msg_time = msg.date.replace(tzinfo=timezone.utc)
        if msg_time < after_ts:
            break

        if not is_trigger(msg.text):
            continue

        forwarded_text = format_forwarded_message(msg)
        msg_hash = hash_message(forwarded_text)

        if is_hash_known(group_id, msg_hash):
            print(f"⚠️ Уже пересылали (хеш): {msg.id}")
            continue

        try:
            await client.send_message(TARGET_GROUP_ID, forwarded_text)
            save_hash(group_id, msg_hash)
            print(f"📤 Переслано: {msg.id}")
        except Exception as e:
            print(f"❌ Ошибка при пересылке: {e}")

async def main():
    now = datetime.now(timezone.utc)
    after = now - timedelta(minutes=PERIOD_MINUTES)
    print(f"🕒 Период: {after} ... {now}")
    print("📥 SOURCE_GROUP_IDS:", SOURCE_GROUP_IDS)
    print(f"📤 TARGET_GROUP_ID: {TARGET_GROUP_ID}")

    async with app:
        try:
            await app.get_chat(TARGET_GROUP_ID)
        except Exception as e:
            print(f"❌ Не удалось получить целевую группу: {e}")
            return

        for group in SOURCE_GROUP_IDS:
            await process_group(app, group, after)

if __name__ == "__main__":
    app.run(main())
