import json, re
from atoms import respond_with_ai, run_query
from utils import save_expense
from models import MessageRequest

def _insert_qualified_message(id, group_link, group_name, tg_user_id, tg_user_name, msg, app_url):
    query = """
        INSERT INTO qualified_messages (
            id, group_link, group_name, tg_user_id, tg_user_name, msg, app_url
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (id, group_link, group_name, tg_user_id, tg_user_name,msg,app_url)
    run_query(query, params)


def _update_qualified_message_with_generic(id, generic_title, generic_description):
    run_query(
        """
        UPDATE qualified_messages
        SET generic_title = %s, generic_description = %s
        WHERE id = %s;
        """,
        (generic_title, generic_description, id)
    )

def _generate_title_description(msg, openai_client):
    prompt = f"""
Ты — помощник по анализу сообщений.

Проанализируй следующее сообщение и верни:
- **Короткий заголовок**, который отражает суть сообщения (generic_title)
- **Краткое описание** содержимого (generic_description), максимум 250 символов

Формат строго: JSON
{{
    "generic_title": "...",
    "generic_description": "..."
}}

Сообщение:
{msg}
"""

    response, in_price, out_price = respond_with_ai(prompt, openai_client, 1500, "gpt-4.1-mini")

    try:
        clean = re.sub(r"^```json|```$", "", response.strip(), flags=re.MULTILINE).strip()
        parsed = json.loads(clean)
        return parsed, in_price, out_price
    except:
        return None

def handle_qualified_message(message: MessageRequest, openai_client):
    _insert_qualified_message(
        message.id,
        message.group_link,
        message.group_name,
        message.tg_user_id,
        message.tg_user_name,
        message.msg,
        message.app_url,
    )
    
    generic_text, in_amount, out_amount = _generate_title_description(message.msg, openai_client)
    save_expense(message.id, "generic_text", in_amount, out_amount)
    
    try:
        message.generic_title = generic_text.get("generic_title") or message.generic_title
        message.generic_description = generic_text.get("generic_description") or message.generic_description
    except:
        pass
    
    _update_qualified_message_with_generic(
        message.id, 
        message.generic_title, 
        message.generic_description
    )




