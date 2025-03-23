import psycopg2
# import requests
import json
import logging
import time
from config import DB_CONFIG, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout) 
    ]
)

while True:
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        print("Connected to PostgreSQL!", flush=True)
        break
    except Exception as e:
        print(f"Error connecting to database: {e}")
        time.sleep(5)

def send_alert(message):
    """Mengirim notifikasi ke Telegram."""
    # url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    # data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    # requests.post(url, data=data)
    logging.info(f"Alert sent: {message}")

def listen_postgres():
    cursor.execute("LISTEN transaction_alert;")
    print("Listening for PostgreSQL notifications...")

    while True:
        conn.poll()
        while conn.notifies:
            notify = conn.notifies.pop(0)
            transaction = json.loads(notify.payload)

            operation = transaction["operation"]
            # print("Database NOTIFY Event:", transaction)
            # logging.info(f"Received event: {transaction}")

            if operation == "INSERT":
                message = (
                    f"INSERT: Transaksi Baru!\n"
                    f"User ID: {transaction['user_id']}\n"
                    f"Amount: {transaction['amount']}\n"
                    f"Status: {transaction['status']}"
                )
                if transaction["amount"] >= 10000000:
                    message += "\n🚨 ada nominal transaksi yang lebih dari 10 juta"
                send_alert(message)

            elif operation == "UPDATE":
                message = (
                    f"UPDATE: Transaksi {transaction['id']}!\n"
                    f"User ID: {transaction['user_id']}\n"
                    f"Amount: {transaction['old_amount']} → {transaction['new_amount']}\n"
                    f"Status: {transaction['old_status']} → {transaction['new_status']}"
                )
                send_alert(message)

            elif operation == "DELETE":
                message = (
                    f"DELETE: Transaksi {transaction['id']}!\n"
                    f"User ID: {transaction['user_id']}\n"
                    f"Amount: {transaction['amount']}\n"
                    f"Status: {transaction['status']}"
                )
                send_alert(message)

if __name__ == "__main__":
    listen_postgres()
