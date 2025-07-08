import asyncio
import hashlib
import os
from pyrogram import Client
from pyrogram.types import Message
from config import API_ID, API_HASH, SESSION_STRING, SOURCE_GROUP_IDS, TARGET_GROUP_ID, TRIGGER_WORDS
from datetime import datetime, timedelta, timezone

PERIOD_MINUTES = 10
MAX_HASHES = 50
BASE_DIR = os.path.dirname(__file__)
HASH_DIR = os.path.join(BASE_DIR, "hashes")

app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

def is_trigger(text):
    return any(word.lower() in text.lower() for word in TRIGGER_WORDS)

def ensure_group_dir(group_id):
    gid = str(group_id).replace("@", "").replace("-", "m")
    path = os.path.join(HASH_DIR, gid)
    os.makedirs(path, exist_ok=True)
    return path

def hash_message(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def get_hash_list_path(group_id):
    return os.path.join(ensure_group_dir(group_id), "hashes.txt")

def load_hash_list(group_id):
    path = get_hash_list_path(group_id)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip()]

def save_hash_list(group_id, hashes):
    path = get_hash_list_path(group_id)
    with open(path, "w") as f:
        f.write("\n".join(hashes[-MAX_HASHES:]))
    print(f"💾 Сохранено {len(hashes[-MAX_HASHES:])} хешей для группы {group_id}")

def is_known_hash(group_id, hash_str):
    return hash_str in load_hash_list(group_id)

def append_hash(group_id, hash_str):
    hashes = load_hash_list(group_id)
    if hash_str not in hashes:
        hashes.append(hash_str)
        save_hash_list(group_id, hashes)

def format_forwarded_message(msg):
    text = msg.text or ""
    text += "\n\n"
    if msg.chat.username:
        text += f"https://t.me/{msg.chat.username}\n"
    elif str(msg.chat.id).startswith("-100"):
        text += f"https://t.me/c/{str(msg.chat.id)[4:]}\n"
    else:
        text += f"{msg.chat.id}\n"
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

        text = format_forwarded_message(msg)
        msg_hash = hash_message(text)

        if is_known_hash(group_id, msg_hash):
            print(f"⚠️ Уже пересылали (хеш): {msg.id}")
            continue

        try:
            await client.send_message(TARGET_GROUP_ID, text)
            append_hash(group_id, msg_hash)
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
