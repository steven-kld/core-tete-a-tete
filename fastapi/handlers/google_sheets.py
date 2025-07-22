import os, re, requests
from atoms import run_query
from dotenv import load_dotenv
from models import MessageRequest, AccountData
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

FERNET_KEY = os.getenv("FERNET_KEY")
fernet = Fernet(FERNET_KEY)

def _get_accounts(group_name, flag):
    # Returns a list of accounts matching group and flag
    results = run_query("""
        SELECT a.*
        FROM accounts a
        JOIN accounts_groups ag ON ag.account_id = a.id
        JOIN groups g ON ag.group_id = g.id
        WHERE g.group_name = %s
          AND ag.flag = %s
    """, (group_name, flag), fetch_all=True)

    accounts = []
    for result in results:
        accounts.append(AccountData(
            id=result["id"],
            bot_chat_id=int(fernet.decrypt(result["bot_chat_id"].encode()).decode()),
            sheet_id=fernet.decrypt(result["sheet_id"].encode()).decode(),
            script_id=fernet.decrypt(result["script_id"].encode()).decode(),
            bot_token=fernet.decrypt(result["bot_token"].encode()).decode()
        ))
    return accounts

def append_job_to_spreadsheet(message: MessageRequest):
    accounts = _get_accounts(message.group_name, message.flags[0])

    for account in accounts:
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

