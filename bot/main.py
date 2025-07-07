import asyncio
from pyrogram import Client
from config import API_ID, API_HASH, SESSION_STRING, SOURCE_GROUP_IDS, TARGET_GROUP_ID, TRIGGER_WORDS
from datetime import datetime, timedelta, timezone
import os
from pyrogram.types import Message

PERIOD_MINUTES = 10

app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

def is_trigger(text):
    return any(word.lower() in text.lower() for word in TRIGGER_WORDS)

def get_id_file(group_id):
    safe_id = str(group_id).replace("@", "").replace("-", "m")
    return f"processed_ids_{safe_id}.txt"

def load_processed_ids(group_id):
    fname = get_id_file(group_id)
    if os.path.exists(fname):
        with open(fname, "r") as f:
            try:
                return set(map(int, f.read().strip().splitlines()))
            except:
                return set()
    return set()

def save_processed_id(group_id, msg_id):
    fname = get_id_file(group_id)
    with open(fname, "a") as f:
        f.write(f"{msg_id}\n")

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

async def process_group(client, group_id):
    processed_ids = load_processed_ids(group_id)
    print(f"\n🔍 Обработка группы: {group_id}, обработано ранее: {len(processed_ids)} сообщений")

    async for msg in client.get_chat_history(group_id, limit=100):
        if not isinstance(msg, Message) or not isinstance(msg.id, int):
            continue

        if msg.id in processed_ids:
            print(f"⏭ msg.id {msg.id} уже обработан")
            continue

        if not msg.text:
            print(f"📭 msg.id {msg.id}: нет текста")
            continue

        if msg.from_user and msg.from_user.is_self:
            print(f"🙋 msg.id {msg.id}: мое сообщение")
            continue

        if is_trigger(msg.text):
            print(f"✅ msg.id {msg.id}: подходит под триггер")
            try:
                forwarded_text = format_forwarded_message(msg)
                await client.send_message(TARGET_GROUP_ID, forwarded_text)
                print(f"📤 Переслано: {msg.text[:40]}...")
            except Exception as e:
                print(f"❌ Ошибка при пересылке: {e}")
        else:
            print(f"🚫 msg.id {msg.id}: не подходит под триггер")

        # Отмечаем как обработанное в любом случае
        save_processed_id(group_id, msg.id)

async def main():
    now = datetime.now(timezone.utc)
    after = now - timedelta(minutes=PERIOD_MINUTES)
    print(f"🕒 Период: {after} ... {now}")
    print("📥 SOURCE_GROUP_IDS:", SOURCE_GROUP_IDS)
    print(f"📤 TARGET_GROUP_ID: {TARGET_GROUP_ID} (type: {type(TARGET_GROUP_ID)})")

    async with app:
        try:
            chat = await app.get_chat(TARGET_GROUP_ID)
            print("ℹ️ Информация о целевой группе:", chat)
        except Exception as e:
            print(f"❌ Не удалось получить целевую группу: {e}")

        for group in SOURCE_GROUP_IDS:
            await process_group(app, group)

if __name__ == "__main__":
    app.run(main())
