import asyncio
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from pyrogram import Client
from pyrogram.types import Message
from config import (
    API_ID,
    API_HASH,
    SESSION_STRING,
    SOURCE_GROUP_IDS,
    TARGET_GROUP_ID,
    TRIGGER_WORDS,
)

# Настройки
PERIOD_MINUTES = 10

# Путь к директории с текущим файлом
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(BASE_DIR, "state")

# Отладочная информация
print(f"\n📂 Текущая рабочая директория: {os.getcwd()}")
print(f"📁 Ожидаемая папка state: {STATE_DIR}")

# Инициализация клиента Pyrogram
app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
)

# Проверка на триггерные слова
def is_trigger(text: str) -> bool:
    return any(word.lower() in text.lower() for word in TRIGGER_WORDS)

# Создание директории состояния, если не существует
def ensure_state_dir():
    os.makedirs(STATE_DIR, exist_ok=True)

# Формирование пути к JSON-файлу состояния
def get_state_file(group_id):
    safe_id = str(group_id).replace("@", "").replace("-", "m")
    return os.path.join(STATE_DIR, f"state_{safe_id}.json")

# Загрузка состояния из файла
def load_group_state(group_id):
    ensure_state_dir()
    path = get_state_file(group_id)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Ошибка чтения state-файла {path}: {e}")
    return {"last_id": 0, "hashes": []}

# Сохранение состояния в файл
def save_group_state(group_id, state):
    ensure_state_dir()
    path = get_state_file(group_id)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f)
    except Exception as e:
        print(f"⚠️ Ошибка записи state-файла {path}: {e}")

# Получение текста из сообщения
def get_text_from_message(msg: Message) -> str:
    return msg.text or msg.caption or ""

# Форматирование текста пересылаемого сообщения
def format_forwarded_message(msg: Message) -> str:
    text = get_text_from_message(msg)
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

# Получение хеша текста
def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# Обработка сообщений в одной группе
async def process_group(client, group_id, after_ts):
    state = load_group_state(group_id)
    last_id = state.get("last_id", 0)
    recent_hashes = state.get("hashes", [])
    max_id = last_id

    print(f"\n🔍 Обработка группы: {group_id}, last_message_id: {last_id}")

    async for msg in client.get_chat_history(group_id, limit=100):
        if not isinstance(msg, Message):
            continue
        if not isinstance(msg.id, int):
            continue
        if msg.id <= last_id:
            break
        if msg.from_user and msg.from_user.is_self:
            continue

        text = get_text_from_message(msg)
        if not text:
            continue

        if is_trigger(text):
            forwarded_text = format_forwarded_message(msg)
            msg_hash = hash_text(forwarded_text)

            if msg_hash in recent_hashes:
                print(f"🔁 Повтор текста, msg.id {msg.id}, не отправляем снова")
                continue

            try:
                await client.send_message(TARGET_GROUP_ID, forwarded_text)
                print(f"📤 Переслано: {text[:40]}...")
                recent_hashes.append(msg_hash)
                recent_hashes = recent_hashes[-50:]  # последние 50 хешей
            except Exception as e:
                print(f"❌ Ошибка при пересылке: {e}")
        else:
            print(f"🚫 msg.id {msg.id}: не по триггеру")

        if msg.id > max_id:
            max_id = msg.id

    if max_id > last_id:
        state["last_id"] = max_id
        state["hashes"] = recent_hashes
        print(f"💾 Сохраняем state: {state}")
        print(f"📄 Файл состояния: {get_state_file(group_id)}")
        save_group_state(group_id, state)

# Главная точка входа
async def main():
    now = datetime.now(timezone.utc)
    after = now - timedelta(minutes=PERIOD_MINUTES)
    print(f"\n🕒 Период: {after} ... {now}")
    print("📥 SOURCE_GROUP_IDS:", SOURCE_GROUP_IDS)
    print(f"📤 TARGET_GROUP_ID: {TARGET_GROUP_ID} (type: {type(TARGET_GROUP_ID)})")

    ensure_state_dir()

    async with app:
        try:
            chat = await app.get_chat(TARGET_GROUP_ID)
            print("ℹ️ Целевая группа:", chat.title or chat.id)
        except Exception as e:
            print(f"❌ Не удалось получить целевую группу: {e}")

        for group in SOURCE_GROUP_IDS:
            await process_group(app, group, after)

# Запуск
if __name__ == "__main__":
    app.run(main())
