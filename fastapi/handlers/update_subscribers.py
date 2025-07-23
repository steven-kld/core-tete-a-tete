from atoms import run_query

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