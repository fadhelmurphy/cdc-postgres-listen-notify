import psycopg2
import json
import logging
import time
import sys
from config import DB_CONFIG

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def connect_db():
    while True:
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.autocommit = True
            logging.info("Connected to PostgreSQL!")
            return conn
        except Exception as e:
            logging.error(f"Error connecting to database: {e}")
            time.sleep(5)

def send_alert(message):
    logging.info(f"Alert sent: {message}")

def process_notification(notify):
    transaction = json.loads(notify.payload)
    operation = transaction.get("operation")
    is_update = "UPDATE" == operation
    user_id, amount, status = transaction.get("user_id"), transaction.get("amount"), transaction.get("status")
    
    messages = {
        "INSERT": (
            f"INSERT: Transaksi Baru!\nUser ID: {user_id}\nAmount: {amount}\nStatus: {status}"
            "\n🚨 ada nominal transaksi yang lebih dari 10 juta"  if amount and amount >= 10_000_000 else ""
            ) if not is_update else "",
        "UPDATE": (
            f"UPDATE: Transaksi {transaction.get('id')}!\nUser ID: {user_id}\n"
            f"Amount: {transaction.get('old_amount')} → {transaction.get('new_amount')}\n"
            f"Status: {transaction.get('old_status')} → {transaction.get('new_status')}"
            ),
        "DELETE": f"DELETE: Transaksi {transaction.get('id')}!\nUser ID: {user_id}\nAmount: {amount}\nStatus: {status}"
    }
    
    send_alert(messages[operation])

def listen_postgres(conn):
    cursor = conn.cursor()
    cursor.execute("LISTEN transaction_alert;")
    logging.info("Listening for PostgreSQL notifications...")
    
    while True:
        conn.poll()
        while conn.notifies:
            process_notification(conn.notifies.pop(0))

if __name__ == "__main__":
    listen_postgres(connect_db())
