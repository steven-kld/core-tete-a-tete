from atoms import respond_with_ai, run_query
from utils import save_expense
from models import MessageRequest
import json, re

def _get_matching_prompts(group_name):
    result = run_query(
        """
        SELECT p.*
        FROM groups g
        JOIN prompts p ON g.prompt_id = p.id
        WHERE g.group_name = %s
        """,
        (group_name,),
        fetch_one=True
    )
    return result if result else False

def _update_flags(message_id, flags):
    run_query(
        """
        UPDATE qualified_messages
        SET flags = %s
        WHERE id = %s;
        """,
        (flags, message_id)
    )

def _if_matches_prompt(msg, prompt_base, openai_client):
    prompt = f"""
{prompt_base}
{msg}
"""
    response, in_amount, out_amount = respond_with_ai(prompt, openai_client, max_tokens=2500, model="gpt-4.1-mini")
    response_clean = response.strip().lower()
    if response_clean == "true":
        result = True
    elif response_clean == "false":
        result = False
    else:
        result = None

    return result, in_amount, out_amount

def _flag_message(msg, flags, openai_client):
    flags_list = '\n'.join([f"{i}. {c}" for i, c in enumerate(flags)])
    prompt = f"""
Ты система категоризации. Для приведенного ниже сообщения выбери только одну наиболее подходящую категорию из списка ниже. Категория должна максимально точно отражать смысл запроса на услугу или товар. Пиши только номер категории из списка, ничего больше, без пояснений.
Выбери 'Не соответствует категории' (номер 0), если сообщение не соотвествует ни одной категории 

Список категорий:
{flags_list}

Сообщение:
{msg}
"""

    response, in_amount, out_amount = respond_with_ai(prompt, openai_client, max_tokens=2500, model="gpt-4.1-mini")
    return response.strip(), in_amount, out_amount

def _detect_direct_ask(msg, flag, openai_client):
    prompt = f"""
Ты — помощник по анализу сообщений.

Проанализируй следующее сообщение и определи, возможно ли в ответ на него предложить услугу **{flag}** или порекомендовать исполнителя услуги **{flag}**

- Отвечай False, если сообщение содержит предложение об оказании этой услуги или рекламу, а не запрос на исполнение этой услуги
- Отвечай True, если в ответ на сообщение можно предложить оказание услуги **{flag}** или порекомендовать человека-исполнителя услуги или компанию-исполнителя

Ответь строго: True или False.

Сообщение:
{msg}
"""
    response, in_price, out_price = respond_with_ai(prompt, openai_client, max_tokens=800, model="gpt-4.1-mini")
    response_clean = response.strip().lower()
    if response_clean == "true":
        result = True
    elif response_clean == "false":
        result = False
    else:
        result = None

    return result, in_price, out_price

def handle_flags(message: MessageRequest, openai_client):
    flags = []
    matching_prompt = _get_matching_prompts(message.group_name)
    
    if matching_prompt == False:
        return flags
   
    matches_prompt, in_amount, out_amount = _if_matches_prompt(message.msg, matching_prompt["rate_prompt"], openai_client)
    
    
    if matches_prompt == True:        
        flag, in_amount_f, out_amount_f = _flag_message(message.msg, matching_prompt["flags"], openai_client)
        in_amount += in_amount_f
        out_amount += out_amount_f
        
        if int(flag) != 0 and flag:
            direct_ask, in_amount_ask, out_amount_ask = _detect_direct_ask(message.msg, flag, openai_client)
            in_amount += in_amount_ask
            out_amount += out_amount_ask
            if direct_ask:
                flags.append(matching_prompt["flags"][int(flag)])
                _update_flags(message.id, flags)
        
    message.flags = flags
    save_expense(message.id, "flag", in_amount, out_amount)
    return flags
