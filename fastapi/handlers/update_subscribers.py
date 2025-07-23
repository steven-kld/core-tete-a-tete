from atoms import run_query
from models import MessageRequest
import os, re, requests
from dotenv import load_dotenv

load_dotenv()
WORKER_URL = os.getenv("WORKER_URL")

def update_subscriber_chat_id(tg_username, chat_id):
    row = run_query(
        """
        UPDATE bot_subscribers
        SET chat_id = %s
        WHERE tg_username = %s
        RETURNING id;
        """,
        (chat_id, tg_username),
        fetch_one=True
    )
    return row is not None


def _get_chat_ids(flag):
    results = run_query("""
        SELECT chat_id
        FROM bot_subscribers
        WHERE flag = %s AND chat_id IS NOT NULL
    """, (flag,), fetch_all=True)

    return [row['chat_id'] for row in results]


def send_bot_alert(message: MessageRequest):
    chat_ids = _get_chat_ids(message.flags[0])
    for chat_id in chat_ids:
        payload = {
            "chat_id": chat_id,
            "message_raw": re.sub(r"[^\w\s#?!.,:+()%/\-\nа-яА-ЯёЁ]", "", message.msg, flags=re.UNICODE),
            "title": message.generic_title,
            "username": message.tg_user_name,
            "app_url": message.app_url
        }

        try:
            requests.post(
                WORKER_URL,
                json=payload,
                timeout=3
            )
        except Exception as e:
            print(f"Failed to notify chat_id={chat_id}: {e}")