import json, re
from atoms import respond_with_ai, run_query
from utils import save_expense
from models import MessageRequest


def _get_matching_prompts(group_name):
    return run_query(
        """
        SELECT a.id AS account_id, a.prompt
        FROM groups g
        JOIN accounts_groups ag ON g.id = ag.group_id
        JOIN accounts a ON ag.account_id = a.id
        WHERE g.group_name = %s;
        """, 
        (group_name,), 
        fetch_all=True
    )

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

Ответь строго:
True — если сообщение подходит
False — если нет

Текст сообщения:
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

def handle_flags(message: MessageRequest, openai_client):
    matching_prompts = _get_matching_prompts(message.group_name)
    flags = []
    
    for prompt in matching_prompts:
        account_id = prompt.get("account_id", None)
        if account_id is None:
            print(f"Skipping prompt with invalid account_id: {prompt}")
            continue
        
        matches_prompt, in_amount, out_amount = _if_matches_prompt(message.msg, prompt["prompt"], openai_client)
        save_expense(message.id, "flag", in_amount, out_amount, account_id=account_id)

        if matches_prompt:
            flags.append(account_id)

    if flags:
        _update_flags(message.id, flags)
