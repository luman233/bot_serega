import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, SESSION_STRING, TRIGGER_WORDS, TARGET_GROUP_ID

# Мапа id -> title для быстрого поиска (обновится при первом пересыле)
group_titles = {}

app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

def message_matches(msg: str) -> bool:
    text = msg.lower()
    return any(word.lower() in text for word in TRIGGER_WORDS)

@app.on_message(filters.group)
async def watcher(client: Client, message: Message):
    if not message.text:
        return
    if message_matches(message.text):
        chat_id = message.chat.id
        chat_title = message.chat.title or str(chat_id)
        group_titles[chat_id] = chat_title

        sender = message.from_user
        username = sender.username if sender and sender.username else (sender.first_name if sender else "Unknown")
        forward_text = (
            f"Переслано из группы: **{chat_title}**\n"
            f"От пользователя: **{username}**\n\n"
            f"Сообщение:\n{message.text}"
        )
        await client.send_message(TARGET_GROUP_ID, forward_text)

if __name__ == "__main__":
    app.run()
