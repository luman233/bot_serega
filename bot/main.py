import asyncio
import os
from datetime import datetime, timedelta, timezone
from pyrogram import Client
from pyrogram.types import Message
from config import API_ID, API_HASH, SESSION_STRING, SOURCE_GROUP_IDS, TRIGGER_WORDS

# 🔒 Числовой ID целевой группы
TARGET_GROUP_ID = -1002854897694

# Количество минут для проверки периода (не критично, просто для отладки)
PERIOD_MINUTES = 10

# Клиент UserBot
app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

def is_trigger(text: str) -> bool:
    return any(word.lower() in text.lower() for word in TRIGGER_WORDS)

def get_id_file(group_id) -> str:
    safe_id = str(group_id).replace("@", "").replace("-", "m")
    return f"processed_ids_{safe_id}.txt"

def load_processed_ids(group_id) -> set:
    fname = get_id_file(group_id)
    if os.path.exists(fname):
        with open(fname, "r") as f:
            try:
                return set(map(int, f.read().strip().splitlines()))
            except:
                return set()
    return set()

def save_processed_id(group_id, msg_id: int):
    fname = get_id_file(group_id)
    with open(fname, "a") as f:
        f.write(f"{msg_id}\n")

def format_forwarded_message(msg: Message) -> str:
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
    print(f"\n🔍 Обработка группы: {group_id}, уже обработано: {len(processed_ids)} сообщений")

    async for msg in client.get_chat_history(group_id, limit=100):
        if not isinstance(msg, Message) or not isinstance(msg.id, int):
            continue

        if msg.id in processed_ids:
            print(f"⏭ Пропущено msg.id {msg.id}: уже обработан")
            continue

        if not msg.text:
            print(f"📭 Пропущено msg.id {msg.id}: нет текста")
            save_processed_id(group_id, msg.id)
            continue

        if msg.from_user and msg.from_user.is_self:
            print(f"🙋 Пропущено msg.id {msg.id}: мое сообщение")
            save_processed_id(group_id, msg.id)
            continue

        if is_trigger(msg.text):
            print(f"✅ Найдено ключевое слово в msg.id {msg.id}")
            try:
                formatted = format_forwarded_message(msg)
                await client.send_message(TARGET_GROUP_ID, formatted)
                print(f"📤 Переслано сообщение: {msg.text[:40]}")
            except Exception as e:
                print(f"❌ Ошибка пересылки msg.id {msg.id}: {e}")

        # Сохраняем как обработанное в любом случае
        save_processed_id(group_id, msg.id)

async def main():
    now = datetime.now(timezone.utc)
    after = now - timedelta(minutes=PERIOD_MINUTES)
    print(f"🕒 Период: {after} ... {now}")
    print("📥 Источник: ", SOURCE_GROUP_IDS)
    print("📤 Целевая группа:", TARGET_GROUP_ID)

    async with app:
        try:
            chat = await app.get_chat(TARGET_GROUP_ID)
            print("ℹ️ Информация о целевой группе:", chat)
        except Exception as e:
            print(f"❌ Не удалось получить чат: {e}")

        for group in SOURCE_GROUP_IDS:
            await process_group(app, group)

if __name__ == "__main__":
    app.run(main())
