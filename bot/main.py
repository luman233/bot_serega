import asyncio
from pyrogram import Client
from config import API_ID, API_HASH, SESSION_STRING, SOURCE_GROUP_IDS, TARGET_GROUP_ID, TRIGGER_WORDS
from datetime import datetime, timedelta, timezone

# Время проверки (10 минут)
PERIOD_MINUTES = 10

app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

def is_trigger(text):
    """Проверка, содержит ли сообщение триггерные слова."""
    return any(word.lower() in text.lower() for word in TRIGGER_WORDS)

async def process_group(client, group_id, after_ts):
    """Обходит историю сообщений в группе после after_ts."""
    async for msg in client.get_chat_history(group_id, limit=100):
        # msg.date — datetime в UTC
        if msg.date.replace(tzinfo=timezone.utc) < after_ts:
            break
        if not msg.text:
            continue
        if msg.from_user and msg.from_user.is_self:
            continue
        if is_trigger(msg.text):
            try:
                await client.send_message(TARGET_GROUP_ID, f"[{msg.chat.title or msg.chat.id}] {msg.text}")
                print(f"Переслано: {msg.text[:40]}")
            except Exception as e:
                print(f"Ошибка при пересылке: {e}")

async def main():
    now = datetime.now(timezone.utc)
    after = now - timedelta(minutes=PERIOD_MINUTES)
    print(f"Период: {after} ... {now}")
    print("SOURCE_GROUP_IDS:", SOURCE_GROUP_IDS)
    print("TARGET_GROUP_ID:", TARGET_GROUP_ID)
    async with app:
        for group in SOURCE_GROUP_IDS:
            print(f"Обработка группы: {group}")
            await process_group(app, group, after)

if __name__ == "__main__":
    asyncio.run(main())
