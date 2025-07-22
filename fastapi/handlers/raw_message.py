import time
from atoms import respond_with_ai, run_query
from utils import save_expense
from models import MessageRequest

def _insert_raw_message(group_link, group_name, msg, tg_user_id, tg_user_name):
    insert_query = """
        INSERT INTO telegram_messages (group_link, group_name, msg, tg_user_id, tg_user_name)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """

    params = (group_link, group_name, msg, tg_user_id, tg_user_name)

    result = run_query(insert_query, params, fetch_one=True)
    return result["id"]

def _update_raw_message(id, makes_sense):
    run_query(
        """
        UPDATE telegram_messages
        SET processed = TRUE, makes_sense = %s
        WHERE id = %s;
        """,
        (makes_sense, id)
        )

def _if_makes_sense(msg, client):
    prompt = f"""
Ты анализируешь сообщение из Telegram-чата.

Ответь True, если на это сообщение можно дать **осмысленный, полезный ответ**, который реально поможет автору или закроет его потребность.

Примеры таких сообщений:
- Автор просит рекомендации, совет, обратную связь
- Автор ищет сервисы, услуги, исполнителей, сотрудников, заказчиков, работу
- Предлагает услуги или продукты, ожидает клиентов или партнёров
- Задает реальный вопрос по теме: работа, законы, жизнь, услуги

НЕ считай полезным:
- Сообщение связано с наркотиками, криптовалютой, проституцией, любой незаконной деятельностью
- Предложение об удаленной работе с большим заработком без ясного описания задач (это мошенники)
- Неполные или неясные фразы
- Обычные разговоры без цели
- Репосты или обращения к ботам
- Сообщения, которые невозможно интерпретировать

Ответь строго: True или False.

Текст:
{msg}
"""
    response, in_price, out_price = respond_with_ai(prompt, client, max_tokens=400, model="gpt-4.1-mini")
    response_clean = response.strip().lower()
    if response_clean == "true":
        result = True
    elif response_clean == "false":
        result = False
    else:
        result = None

    return result, in_price, out_price

def handle_raw_message(message: MessageRequest, openai_client):
    id = _insert_raw_message(
        message.group_link, 
        message.group_name, 
        message.msg, 
        message.tg_user_id, 
        message.tg_user_name
    )
    message.id = id
    makes_sense, in_amount, out_amount = _if_makes_sense(message, openai_client)
    save_expense(message.id, "makes_sense", in_amount, out_amount)
    print(makes_sense)
    if makes_sense not in [True, False]:
        time.sleep(7)
        makes_sense, in_amount, out_amount = _if_makes_sense(message, openai_client)
        save_expense(message.id, "makes_sense", in_amount, out_amount)
    
    if makes_sense in [True, False]:
        message.makes_sense = makes_sense
        _update_raw_message(message.id, makes_sense)
        message.processed = True
    else:
        print("Message makes no sense")


