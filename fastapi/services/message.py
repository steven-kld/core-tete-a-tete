from handlers import handle_raw_message, handle_qualified_message, handle_flags
from models import MessageRequest

def process_message(message: MessageRequest, openai_client):
    handle_raw_message(message, openai_client)
    
    if message.makes_sense == False:
        return
    
    handle_qualified_message(message, openai_client)

    handle_flags(message, openai_client)
    