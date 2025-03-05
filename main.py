from telethon import TelegramClient, events
import sqlite3
import asyncio
import os

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone_number = os.getenv('PHONE_NUMBER')
source_group = os.getenv('SOURCE_GROUP')
target_group = os.getenv('TARGET_GROUP')

db_path = os.path.join('data', 'news.db')
os.makedirs('data', exist_ok=True)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS published_news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER UNIQUE
)
''')
conn.commit()

client = TelegramClient('session_file', api_id, api_hash)

async def check_missed_messages():
    """
    Функция для проверки пропущенных сообщений.
    """
    while True:
        try:
            messages = await client.get_messages(source_group, limit=10)
            for message in messages:
                message_id = message.id

                cursor.execute('SELECT message_id FROM published_news WHERE message_id = ?', (message_id,))
                if cursor.fetchone() is None:
                    await client.send_message(target_group, message)
                    
                    cursor.execute('INSERT INTO published_news (message_id) VALUES (?)', (message_id,))
                    conn.commit()
                    print(f"Пропущенная новость {message_id} опубликована в целевой группе.")
                else:
                    print(f"Новость {message_id} уже была опубликована ранее.")
        except Exception as e:
            print(f"Ошибка при проверке пропущенных сообщений: {e}")

        await asyncio.sleep(300)  # 300 секунд = 5 минут

@client.on(events.NewMessage(chats=source_group))
async def handler(event):
    """
    Обработчик новых сообщений.
    """
    message_id = event.message.id

    cursor.execute('SELECT message_id FROM published_news WHERE message_id = ?', (message_id,))
    if cursor.fetchone() is None:
        await client.send_message(target_group, event.message)
        
        cursor.execute('INSERT INTO published_news (message_id) VALUES (?)', (message_id,))
        conn.commit()
        print(f"Новость {message_id} опубликована в целевой группе.")
    else:
        print(f"Новость {message_id} уже была опубликована ранее.")

async def main():
    """
    Основная функция для запуска клиента и задач.
    """

    asyncio.create_task(check_missed_messages())

    await client.start(phone_number)
    print("Клиент запущен. Ожидание новых сообщений...")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
