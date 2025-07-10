from models import MessageRequest
from services import process_message
from atoms import  init_openai, run_query

openai_client = init_openai()

last_messages = run_query(
    """
    SELECT *
    FROM telegram_messages
    WHERE makes_sense = false
    AND id < 38000
    ORDER BY created_at DESC
    LIMIT 1000;
    """, fetch_all=True
)

print(last_messages[0])
for m in last_messages:
    message = MessageRequest(
        id=m.get("id"),
        group_link=m.get("group_link"),
        group_name=m.get("group_name", "Unknown"),
        msg=m.get("msg"),
        tg_user_id=m.get("tg_user_id"),
        tg_user_name=m.get("tg_user_name", "Unknown")
    )
    print("###########")
    print(message.msg[:100])
    process_message(message, openai_client)
