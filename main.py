from telethon import TelegramClient, events
import sqlite3
import asyncio
import os
import re

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
    message_id INTEGER UNIQUE,
    publish_date DATE DEFAULT CURRENT_DATE
)
''')
conn.commit()

client = TelegramClient(session_file, api_id, api_hash)


def fix_markdown_formatting(text):
    link_pattern = re.compile(r'\[(.*?)\]\((.*?)\)')

    def replace_link(match):
        link_text = match.group(1)
        link_url = match.group(2)

        clean_text = link_text.replace('**', '').replace('__', '')

        return f'**[{clean_text}]({link_url})**'

    text = link_pattern.sub(replace_link, text)

    lines = text.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('>'):
            lines[i] = f'>{line.strip()[1:]}'

    return '\n'.join(lines)


@client.on(events.NewMessage(chats=source_group))
async def handler(event):
    try:
        message_id = event.message.id
        with conn:
            cursor.execute(
                'SELECT 1 FROM published_news WHERE message_id = ? or date(publish_date) = date("now")',
                (message_id,))
            if cursor.fetchone() is None:
                message_text = event.message.text
                if message_text or event.message.media:
                    if event.message.media:
                        media_path = await event.message.download_media()
                        fixed_text = fix_markdown_formatting(message_text)
                        await client.send_file(
                            target_group,
                            media_path,
                            caption=fixed_text,
                            parse_mode='md'
                        )
                        os.remove(media_path)
                    else:
                        fixed_text = fix_markdown_formatting(message_text)
                        await client.send_message(
                            target_group,
                            fixed_text,
                            parse_mode='md'
                        )

                    cursor.execute('INSERT INTO published_news (message_id, publish_date) VALUES (?, date("now"))',
                                   (message_id,))
                    conn.commit()
                    print(f"Новость {message_id} опубликована в целевой группе.")
                else:
                    print(f"Новость {message_id} не содержит текста или медиа.")
            else:
                print(f"Новость {message_id} уже была опубликована ранее.")
    except Exception as e:
        print(f"Ошибка при обработке сообщения {message_id}: {e}")


async def main():
    await client.start(phone=phone_number)
    print("Клиент запущен. Ожидание новых сообщений...")
    await client.run_until_disconnected()


with client:
    client.loop.run_until_complete(main())