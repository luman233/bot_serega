import asyncio
from pyrogram import Client, filters
from config import API_ID, API_HASH, SESSION_STRING, SOURCE_GROUP_IDS, TARGET_GROUP_ID, TRIGGER_WORDS

app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

def is_trigger(text):
    """Проверка, содержит ли сообщение триггерные слова."""
    return any(word.lower() in text.lower() for word in TRIGGER_WORDS)

@app.on_message(filters.text)
async def handle_message(client, message):
    # Проверяем, что сообщение из нужной исходной группы
    src_id = message.chat.id
    # Username группы в Pyrogram — message.chat.username
    src_username = getattr(message.chat, "username", None)
    # Проверим оба варианта (id и username)
    src_candidates = [src_id]
    if src_username:
        src_candidates.append(src_username)
    # Если SOURCE_GROUP_IDS пуст — реагировать на ВСЕ группы
    if SOURCE_GROUP_IDS:
        if not any(s in SOURCE_GROUP_IDS for s in src_candidates):
            return
    # Не пересылать свои собственные сообщения (userbot)
    if message.from_user and message.from_user.is_self:
        return
    # Проверяем на наличие триггерного слова
    if is_trigger(message.text):
        try:
            await client.send_message(TARGET_GROUP_ID, message.text)
            print(f"Сообщение переслано из {src_id} в {TARGET_GROUP_ID}: {message.text[:40]}")
        except Exception as e:
            print(f"Ошибка при пересылке: {e}")

if __name__ == "__main__":
    # Для отладки выводим параметры
    print("SOURCE_GROUP_IDS:", SOURCE_GROUP_IDS)
    print("TARGET_GROUP_ID:", TARGET_GROUP_ID)
    print("TRIGGER_WORDS:", TRIGGER_WORDS)
    app.run()
