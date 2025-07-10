from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os, json
from dotenv import load_dotenv
from models import MessageRequest
from config import CHAT_BLACKLIST
from services import process_message
load_dotenv()

app = FastAPI()

@app.post("/api/msg")
async def receive_msg(data: MessageRequest):
    if data.group_name not in CHAT_BLACKLIST:
        process_message(data)
        
    return JSONResponse(content={"status": "success", "message": "Data received successfully"}, status_code=200)