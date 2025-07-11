import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from atoms import run_query
load_dotenv()

FERNET_KEY = os.getenv("FERNET_KEY")
fernet = Fernet(FERNET_KEY)
def _get_account(account_id):
    result = run_query("""
    SELECT * FROM accounts WHERE id = %s
    """, (account_id,), fetch_one=True)

    print(
        account_id,
        int(fernet.decrypt(result["bot_chat_id"].encode()).decode()),
        fernet.decrypt(result["sheet_id"].encode()).decode(),
        fernet.decrypt(result["script_id"].encode()).decode(),
        fernet.decrypt(result["bot_token"].encode()).decode()
    )
_get_account(2)


# from atoms import init_openai
# from services import process_message
# from models import MessageRequest

# msg = """
# Коллеги, добрый день!
# Подскажите, пожалуйста, обязательно ли проходить обучение по пожарной безопасности для офисных сотрудников, если у нас менее 50 человек?
# И если да, то какие документы нужно оформить после прохождения? Спасибо!
# """

# message = MessageRequest(
#     group_link="group_link",
#     group_name="Чат | Электрики 🔌💡",
#     msg=msg,
#     tg_user_id=123456,
#     tg_user_name="tg_user_name"
# )
# openai_client = init_openai()

# process_message(message, openai_client)


# FERNET_KEY = os.getenv("FERNET_KEY")
# fernet = Fernet(FERNET_KEY)

# chat_id = 461589951 # Nikolay
# bot_token = ""
# sheet_id  = ""
# script_id = ""


# encrypted_token = fernet.encrypt(bot_token.encode()).decode()
# print(encrypted_token)
# decrypted_token = fernet.decrypt(encrypted_token.encode()).decode()
# print(decrypted_token)

