from fastapi import FastAPI
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from atoms import init_openai
from models import MessageRequest
from config import CHAT_BLACKLIST
from services import process_message
load_dotenv()

app = FastAPI()
openai_client = init_openai()

@app.post("/api/msg")
async def receive_msg(data: MessageRequest):
    if data.group_name not in CHAT_BLACKLIST:
        process_message(data, openai_client)
        
    return JSONResponse(content={"status": "success", "message": "Data received successfully"}, status_code=200)