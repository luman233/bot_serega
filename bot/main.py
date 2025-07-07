import asyncio
from datetime import datetime, timedelta, timezone

from pyrogram import Client
from config import (
    API_ID, API_HASH, SESSION_STRING,
    TRIGGER_WORDS, TARGET_GROUP_ID, SOURCE_GROUP_IDS
)

def message_matches(msg: str) -> bool:
    text = msg.lower()
    return any(word.lower() in text for word in TRIGGER_WORDS)

async def process_messages():
    app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
    await app.start()
    now = datetime.now(timezone.utc)
    time_window = now - timedelta(minutes=10)

    for group_id in SOURCE_GROUP_IDS:
        async for msg in app.get_chat_history(group_id, offset_date=now):
            if msg.date.replace(tzinfo=timezone.utc) < time_window:
                break
            if not msg.text:
                continue
            if message_matches(msg.text):
                sender = msg.from_user
                username = sender.username if sender and sender.username else (sender.first_name if sender else "Unknown")
                chat = await app.get_chat(group_id)
                chat_title = chat.title or str(group_id)
                forward_text = (
                    f"Переслано из группы: **{chat_title}**\n"
                    f"От пользователя: **{username}**\n\n"
                    f"Сообщение:\n{msg.text}"
                )
                await app.send_message(TARGET_GROUP_ID, forward_text)
    await app.stop()

if __name__ == "__main__":
    asyncio.run(process_messages())
