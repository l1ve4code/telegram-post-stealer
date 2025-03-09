from telethon import TelegramClient, events
import sqlite3
import asyncio
import os

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone_number = os.getenv('PHONE_NUMBER')
source_group = int(os.getenv('SOURCE_GROUP'))
target_group = int(os.getenv('TARGET_GROUP'))

session_file = 'session_file'

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

client = TelegramClient(session_file, api_id, api_hash)


async def check_missed_messages():
    while True:
        try:
            messages = await client.get_messages(source_group, limit=10)
            for message in messages:
                message_id = message.id

                with conn:
                    cursor.execute('SELECT message_id FROM published_news WHERE message_id = ?', (message_id,))
                    if cursor.fetchone() is None:
                        message_text = message.text
                        if message_text or message.media:
                            if message.media:
                                media_path = await message.download_media()
                                await client.send_file(
                                    target_group,
                                    media_path,
                                    caption=message_text,
                                    parse_mode='md'
                                )
                                os.remove(media_path)
                            else:
                                await client.send_message(
                                    target_group,
                                    message_text,
                                    parse_mode='md'
                                )

                            cursor.execute('INSERT INTO published_news (message_id) VALUES (?)', (message_id,))
                            conn.commit()
                            print(f"Новость {message_id} опубликована в целевой группе.")
                        else:
                            print(f"Новость {message_id} не содержит текста или медиа.")
                    else:
                        print(f"Новость {message_id} уже была опубликована ранее.")
        except Exception as e:
            print(f"Ошибка при проверке пропущенных сообщений: {e}")

        await asyncio.sleep(300)


@client.on(events.NewMessage(chats=source_group))
async def handler(event):
    try:
        message_id = event.message.id

        with conn:
            cursor.execute('SELECT message_id FROM published_news WHERE message_id = ?', (message_id,))
            if cursor.fetchone() is None:
                message_text = event.message.text
                if message_text or event.message.media:
                    if event.message.media:
                        media_path = await event.message.download_media()
                        await client.send_file(
                            target_group,
                            media_path,
                            caption=message_text,
                            parse_mode='md'
                        )
                        os.remove(media_path)
                    else:
                        await client.send_message(
                            target_group,
                            message_text,
                            parse_mode='md'
                        )

                    cursor.execute('INSERT INTO published_news (message_id) VALUES (?)', (message_id,))
                    conn.commit()
                    print(f"Новость {message_id} опубликована в целевой группе.")
                else:
                    print(f"Новость {message_id} не содержит текста или медиа.")
            else:
                print(f"Новость {message_id} уже была опубликована ранее.")
    except Exception as e:
        print(f"Ошибка при обработке сообщения {message_id}: {e}")


async def main():
    asyncio.create_task(check_missed_messages())

    await client.start(phone=phone_number)
    print("Клиент запущен. Ожидание новых сообщений...")
    await client.run_until_disconnected()


with client:
    client.loop.run_until_complete(main())