import asyncio
from pyrogram import Client
from config import API_ID, API_HASH, SESSION_STRING, SOURCE_GROUP_IDS, TARGET_GROUP_ID, TRIGGER_WORDS
from datetime import datetime, timedelta, timezone
import os

PERIOD_MINUTES = 10

app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

def is_trigger(text):
    return any(word.lower() in text.lower() for word in TRIGGER_WORDS)

def get_last_id_file(group_id):
    safe_id = str(group_id).replace("@", "").replace("-", "m")
    return f"last_message_id_{safe_id}.txt"

def load_last_id(group_id):
    fname = get_last_id_file(group_id)
    if os.path.exists(fname):
        with open(fname, "r") as f:
            try:
                return int(f.read().strip())
            except:
                return 0
    return 0

def save_last_id(group_id, msg_id):
    fname = get_last_id_file(group_id)
    with open(fname, "w") as f:
        f.write(str(msg_id))

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
    last_id = load_last_id(group_id)
    max_id = last_id
    print(f"Обработка группы: {group_id}, last_message_id: {last_id}")
    async for msg in client.get_chat_history(group_id, limit=100):
        if not hasattr(msg, "message_id") or msg.message_id is None:
            print("Нет message_id")
            continue
        if msg.message_id <= last_id:
            print(f"msg_id {msg.message_id} <= last_id {last_id}")
            break
        if not msg.text:
            print(f"msg_id {msg.message_id}: нет текста")
            continue
        if msg.from_user and msg.from_user.is_self:
            print(f"msg_id {msg.message_id}: мое же сообщение")
            continue
        if is_trigger(msg.text):
            print(f"msg_id {msg.message_id}: подходит под триггер")
            try:
                forwarded_text = format_forwarded_message(msg)
                await client.send_message(
                    TARGET_GROUP_ID,
                    forwarded_text
                )
                print(f"Переслано: {msg.text[:40]}")
            except Exception as e:
                print(f"Ошибка при пересылке: {e}")
        else:
            print(f"msg_id {msg.message_id}: не подходит под триггер")
        if msg.message_id > max_id:
            max_id = msg.message_id
    if max_id > last_id:
        save_last_id(group_id, max_id)

async def main():
    now = datetime.now(timezone.utc)
    after = now - timedelta(minutes=PERIOD_MINUTES)
    print(f"Период: {after} ... {now}")
    print("SOURCE_GROUP_IDS:", SOURCE_GROUP_IDS)
    print(f"TARGET_GROUP_ID: {TARGET_GROUP_ID} (type: {type(TARGET_GROUP_ID)})")
    async with app:
        try:
            chat = await app.get_chat(TARGET_GROUP_ID)
            print("Информация о целевой группе:", chat)
        except Exception as e:
            print(f"Не удалось получить целевую группу: {e}")
        for group in SOURCE_GROUP_IDS:
            await process_group(app, group, after)

if __name__ == "__main__":
    app.run(main())
