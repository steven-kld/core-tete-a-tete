import os, re, requests
from atoms import run_query
from dotenv import load_dotenv
from models import MessageRequest, AccountData
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

FERNET_KEY = os.getenv("FERNET_KEY")
fernet = Fernet(FERNET_KEY)

def _get_account(account_id):
    result = run_query("""
    SELECT * FROM accounts WHERE id = %s
    """, (account_id,), fetch_one=True)

    return AccountData(
        id=account_id,
        bot_chat_id=int(fernet.decrypt(result["bot_chat_id"].encode()).decode()),
        sheet_id=fernet.decrypt(result["sheet_id"].encode()).decode(),
        script_id=fernet.decrypt(result["script_id"].encode()).decode(),
        bot_token=fernet.decrypt(result["bot_token"].encode()).decode()
    )

def append_job_to_spreadsheet(message: MessageRequest, account_id):
    account = _get_account(account_id)

    url = f"https://script.google.com/macros/s/{account.script_id}/exec"
    payload = {
        "sheet_id": account.sheet_id,
        "id": message.id,
        "message": re.sub(r"[^\w\s#?!.,:+()%/\-\nа-яА-ЯёЁ]", "", message.msg, flags=re.UNICODE),
        "title": message.generic_title,
        "description": message.generic_description,
        "app_url": message.app_url,
        "group_name": message.group_name,
        "username": message.tg_user_name,
        "chat_id": account.bot_chat_id,
        "token": account.bot_token
    }

    response = requests.post(url, data=payload)
    print(response.status_code)
    print(response.text)
    try:
        data = response.json()
        if data.get("success"):
            print("✅ Inserted successfully")
        else:
            print(f"❌ Error: {data.get('error')}")
    except Exception as e:
        print("❌ Failed to parse response:", e)

