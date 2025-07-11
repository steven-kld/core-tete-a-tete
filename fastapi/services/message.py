from handlers import handle_raw_message, handle_qualified_message, handle_flags, append_job_to_spreadsheet
from models import MessageRequest

def process_message(message: MessageRequest, openai_client):
    handle_raw_message(message, openai_client)
    
    if message.makes_sense == False:
        return
    
    handle_qualified_message(message, openai_client)

    flags = handle_flags(message, openai_client)

    for flag in flags:
        append_job_to_spreadsheet(message, flag)