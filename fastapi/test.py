# from handlers import send_bot_alert
# from models import MessageRequest
# from datetime import datetime

# test_message = MessageRequest(
#     id=66539,
#     created_at=datetime.fromisoformat("2025-07-22 08:57:56.517"),
#     processed=True,
#     makes_sense=True,
#     flags=["Туризм, экскурсии, трансфер, водитель"],
#     group_link="https://t.me/health_ge",
#     group_name="Медицина 💊 Грузия",
#     tg_user_id=240046008,
#     tg_user_name="q_pokrovsky",
#     msg="Hi this is my msg",
#     app_url="tg://user?id=240046008",
#     generic_title="Поиск независимого эксперта по медстрахованию в Грузии",
#     generic_description="Ищется независимый специалист по медицинскому страхованию в Грузии, который сможет объективно проконсультировать, раскрыть скрытые условия страховок и помочь выбрать оптимальный вариант без влияния страховых компаний."
# )

# send_bot_alert(test_message)

# import os, json
# from cryptography.fernet import Fernet
# from dotenv import load_dotenv
# from atoms import run_query, init_openai, respond_with_ai
# load_dotenv()
# from handlers import handle_flags, append_job_to_spreadsheet
# openai_client = init_openai()
# from models import MessageRequest
# from datetime import datetime


# msg = (
#     "Привет! Знаете ли вы специалиста по мед. страхованию в Грузии? \n\n"
#     "Я ищу не представителя компании, а независимого эксперта который может проконсультировать, который знает местный рынок\n\n"
#     "Потому что консультанты в страховых - это не консультанты, а менеджеры по продажам, и платит им страховая за проданные страховки. А я ищу эксперта, который может наоборот рассказать про подводные камни всех страховых и объяснить какую и почему страховку лучше выбрать и как ей правильно пользоваться, и как общаться со страховой\n\n"
#     "Делать свой анализ неэффективно, потому что страховые специально усложняют условия и договор, и создают скрытые неочевидные условия, которые сложно выяснить даже при общении с менеджером\n\n"
#     "Тут нужен именно компетентный человек, который имеет опыт работы со страховыми но не зависит от них"
# )

# test_message = MessageRequest(
#     id=66539,
#     created_at=datetime.fromisoformat("2025-07-22 08:57:56.517"),
#     processed=False,
#     makes_sense=True,
#     flags=[],
#     group_link="https://t.me/health_ge",
#     group_name="Медицина 💊 Грузия",
#     tg_user_id=240046008,
#     tg_user_name="q_pokrovsky",
#     msg=msg,
#     app_url="tg://user?id=240046008",
#     generic_title="Поиск независимого эксперта по медстрахованию в Грузии",
#     generic_description="Ищется независимый специалист по медицинскому страхованию в Грузии, который сможет объективно проконсультировать, раскрыть скрытые условия страховок и помочь выбрать оптимальный вариант без влияния страховых компаний."
# )



# handle_flags(test_message, openai_client)
# print(test_message.flags)

# for flag in test_message.flags:
#     append_job_to_spreadsheet(test_message)





# FERNET_KEY = os.getenv("FERNET_KEY")
# fernet = Fernet(FERNET_KEY)

# def _get_valid():
#     return run_query("""
#     SELECT msg, created_at, group_name, id
#     FROM qualified_messages
#     WHERE group_name IN (
        # 'ТБИЛИСИ 🇬🇪 ЧАТ | Грузия',
        # 'БАТУМИ 《🇬🇪🦄》ЧАТ | Грузия',
        # 'Кобулети live чат 🇬🇪',
        # 'САБУРТАЛО | Тбилиси',
        # 'ВАКЕ | Тбилиси'
#     )
#     ORDER BY created_at
#     """, (), fetch_all=True)

# valid = _get_valid()

# rate_prompt = f"""
# Ты анализируешь сообщение из Telegram.
# Твоя задача — точно определить, является ли это сообщение прямым запросом на услугу, специалиста, товар или что-то, что подразумевает явное намерение заказать платную услугу.

# 1. Сообщения, содержащие информацию о криптовалюте, наркотиках, мошенничестве или любую другую подозрительную активность, должны быть отклонены.
# 2. Сообщения, которые являются рекламой или продвижением услуг (например, предложения купить или заказать услуги без явного запроса), должны быть отклонены.

# Ответь **true**, если сообщение прямо и явно запрашивает услугу, контакт специалиста, товар или услугу с четким намерением получить платную помощь.
# Ответь **false**, если сообщение не содержит четкого запроса на услугу или не подразумевает намерение заказать платную услугу, а также если оно связано с криптовалютой, наркотиками, мошенничеством или рекламой.

# Ответь только **true** или **false** на основе сообщения:
# """


# valid_messages = []

# # Function to process each message through GPT
# for msg in valid:
#     # Modify the prompt to fit the new classification categories
#     prompt = rate_prompt + f"\n\nТекст сообщения:\n{msg.get('msg')}"
    
#     # Process the message through GPT
#     res, in_price, out_price = respond_with_ai(
#         prompt,
#         openai_client,
#         500,
#         "gpt-4.1-mini"
#     )
    
#     # Handle the response: If it's classified as a valid service request, store the result
#     if res.lower() != 'false':  # Any non-False classification
#         print(f"Classified message: {msg.get('msg')[:100]}")
#         valid_messages.append({
#             "msg": msg.get("msg"),
#             "classification": res,
#             "date": str(msg.get("created_at")),
#             "group": msg.get("group_name"),
#             "id": msg.get("id")
#         })

# # Save the valid classified messages to a JSON file
# with open('valid_messages_true.json', 'w', encoding='utf-8') as json_file:
#     json.dump(valid_messages, json_file, ensure_ascii=False, indent=4)


# import pandas as pd
# import json

# niches = [
#     "Не соответствует категории",
#     "Туризм, экскурсии, трансфер, водитель",
#     "Логистика, доставка, посылки",
#     "Страховка авто, жизни, страховые услуги",
#     "Ремонт автомобилей и автозапчасти",
#     "Аренда автомобиля, скутера, мопеда",
#     "Аренда, продажа недвижимости",
#     "Уборка квартир, клининг, вывоз мусора",
#     "Ремонт дома, кваритры, строительные услуги",
#     "Обмен денег, денежные переводы",
#     "Юридические и нотариальные услуги",
#     "Услуги бухгалтера, ИП, безнес",
#     "Ремонт и обслуживание техники",
#     "Продажа, аренда и покупка товаров",
#     "Животные, услуги для животных",
#     "Крой, услуги швеи, текстиль",
#     "Бьюти услуги, красота и здоровье",
#     "Медицина, медицинские услуги",
#     "Проведение мероприятий, фотограф, кейтеринг, ведущий"
# ]

# with open('valid_messages_true.json', 'r', encoding='utf-8') as file:
#     data = json.load(file)

# df = pd.DataFrame(data)

# def build_category_prompt(categories, msg):
#     # Create numbered list from array
#     categories_list = '\n'.join([f"{i}. {c}" for i, c in enumerate(categories)])
#     prompt = f"""
# Ты система категоризации. Для приведенного ниже сообщения выбери только одну наиболее подходящую категорию из списка ниже. Категория должна максимально точно отражать смысл запроса на услугу или товар. Пиши только номер категории из списка, ничего больше, без пояснений.
# Выбери 'Не соответствует категории' (номер 0), если сообщение не соотвествует ни одной категории 

# Список категорий:
# {categories_list}

# Сообщение:
# {msg}
# """
#     return prompt


# def detect_niche(msg):
#     prompt = build_category_prompt(niches, msg)
#     res, *_ = respond_with_ai(
#         prompt,
#         openai_client,
#         150,
#         "gpt-4.1-mini"
#     )
#     print(res)
#     return res.strip()

# df["niche"] = df["msg"].apply(detect_niche)

# # Save result
# df.to_json('valid_messages_with_niche.json', orient='records', force_ascii=False, indent=2)

# with open('valid_messages_with_niche.json', 'r', encoding='utf-8') as file:
#     data = json.load(file)

# df = pd.DataFrame(data)

# df['category_name'] = df['niche'].apply(lambda x: niches[int(x)])

# # Count
# cat_counts = df['category_name'].value_counts()


# filtered = []

# for i, row in df.iterrows():
#     if niches[int(row['niche'])] in [
#         "Туризм, экскурсии, трансфер, водитель",
#         "Аренда, продажа недвижимости",
#         "Аренда автомобиля, скутера, мопеда",
#     ]:
#         filtered.append({
#             "msg": row["msg"],
#             "category_name": row["category_name"],
#             "date": row["date"],
#             "value": 0
#         })

# with open('filtered_valid_messages_niche.json', 'w', encoding='utf-8') as f:
#     json.dump(filtered, f, ensure_ascii=False, indent=2)



# with open('filtered_valid_messages_with_named_niche.json', 'r', encoding='utf-8') as file:
#     data = json.load(file)


# filtered_df = pd.DataFrame(data)

# # Count messages per category
# counts = filtered_df.groupby("category_name")["msg"].count()

# # Sum "value" per category (if you start changing value >0)
# sums = filtered_df.groupby("category_name")["value"].sum()

# stats = filtered_df.groupby("category_name").agg(
#     count=("msg", "count"),
#     value_sum=("value", "sum")
# )
# stats["avg_value"] = stats["value_sum"] / stats["count"]
# stats["lead_price"] = stats["avg_value"] / 200
# stats["expected_revenue"] = stats["value_sum"] / 200
# print(stats)


# with open('filtered_valid_messages_niche_with_values.json', 'r', encoding='utf-8') as f:
#     data = json.load(f)

# df = pd.DataFrame(data)

# # Extract date (YYYY-MM-DD)
# df['date_only'] = df['date'].str[:10]

# # Filter for July 18, 2025
# df_filtered = df[df['date_only'] == '2025-07-18']

# # Sum value per category for this date
# cat_sums = df_filtered.groupby('category_name')['value'].sum()

# print(cat_sums)