from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from atoms import init_openai
from models import MessageRequest
from config import CHAT_BLACKLIST
from services import process_message
from handlers import update_subscriber_chat_id
load_dotenv()

app = FastAPI()
openai_client = init_openai()

@app.post("/api/msg")
async def receive_msg(data: MessageRequest):
    if data.group_name not in CHAT_BLACKLIST:
        process_message(data, openai_client)
        
    return JSONResponse(content={"status": "success", "message": "Data received successfully"}, status_code=200)

@app.post("/api/bot/start")
async def receive_msg(request: Request):
    data = await request.json()
    print("Received body:", data)
    tg_message = data.get("tg", {}).get("message", {})
    tg_username = tg_message.get("from", {}).get("username")
    chat_id = str(tg_message.get("chat", {}).get("id"))

    res = update_subscriber_chat_id(tg_username, chat_id)

    return JSONResponse(content={"status": res}, status_code=200)