import os

DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB", "bankdb"),
    "user": os.getenv("POSTGRES_USER", "admin"),
    "password": os.getenv("POSTGRES_PASSWORD", "admin"),
    "host": os.getenv("POSTGRES_HOST", "postgres"),  # Sesuai service name di docker-compose yak ajg
    "port": os.getenv("POSTGRES_PORT", "5432")
}

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID")
