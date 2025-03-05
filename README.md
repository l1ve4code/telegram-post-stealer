# telegram-post-stealer

## About

- **Purpose**: Automatically forward news messages from one Telegram group to another.
- **Key Features**:
  - Fetches new messages from a source Telegram group.
  - Forwards messages to a target Telegram group.
  - Prevents duplicate forwarding using SQLite for message tracking.
  - Handles network interruptions by periodically checking for missed messages.

### Technologies

* Language: **Python**
* Libraries: **Telethon, SQLite3, asyncio**
* Database: **SQLite**
* Deployment: **Docker, Docker Compose**
* API: **Telegram API**

## Installing

### Clone the Project

```shell
git clone https://github.com/live4code/telegram-post-stealer.git
cd telegram-news-forwarder
```

### Set Your Values in `docker-compose.yml`

Replace the placeholders with your Telegram API credentials and group details:

```yaml
services:
  telegram-bot:
    build: .
    container_name: telegram-bot
    network_mode: host
    volumes:
      - ./data:/app/data
    environment:
      - API_ID=YOUR_API_ID
      - API_HASH=YOUR_API_HASH
      - PHONE_NUMBER=YOUR_PHONE_NUMBER
      - SOURCE_GROUP=SOURCE_GROUP_USERNAME_OR_ID
      - TARGET_GROUP=TARGET_GROUP_USERNAME_OR_ID
    restart: unless-stopped
```

### Replace Placeholders in the Script

If you're not using Docker, update the following variables in the script (`main.py`):

```python
api_id = 'YOUR_API_ID'
api_hash = 'YOUR_API_HASH'
phone_number = 'YOUR_PHONE_NUMBER'
source_group = 'SOURCE_GROUP_USERNAME_OR_ID'
target_group = 'TARGET_GROUP_USERNAME_OR_ID'
```

## Running the Project

### Using Docker Compose

1. Build and start the container:

   ```shell
   docker-compose up --build
   ```

2. Stop the container:

   ```shell
   docker-compose down
   ```

### Running Locally

1. Install dependencies:

   ```shell
   pip install -r requirements.txt
   ```

2. Run the script:

   ```shell
   python main.py
   ```

## How It Works

1. **Fetching Messages**:
   - The script listens for new messages in the source Telegram group using the `Telethon` library.
   - If a new message is detected, it checks whether the message has already been forwarded using an SQLite database.

2. **Forwarding Messages**:
   - If the message is new, it forwards the message to the target group.
   - The message ID is stored in the SQLite database to prevent duplicates.

3. **Handling Network Issues**:
   - If the connection is lost, the script periodically checks the last 10 messages in the source group and forwards any missed messages.

4. **Persistent Storage**:
   - The SQLite database (`news.db`) is stored in the `data` folder, ensuring that message IDs are preserved even after the container is restarted.

## Author

* Telegram: **[@live4code](https://t.me/live4code)**
* Email: **steven.marelly@gmail.com**

Good luck with your Telegram news forwarding! 🚀
