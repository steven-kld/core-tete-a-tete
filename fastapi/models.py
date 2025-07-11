from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from datetime import datetime

class AccountData(BaseModel):
    id: int
    bot_chat_id: int
    sheet_id: str
    script_id: str
    bot_token: str

class MessageRequest(BaseModel):
    # Metadata
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    processed: bool = False
    makes_sense: Optional[bool] = None
    flags: List[str] = Field(default_factory=list)
    # Telegram data
    group_link: Optional[str] = None
    group_name: str = "Unknown Group"
    tg_user_id: Optional[int] = None
    tg_user_name: str = "Unknown"
    msg: str = ""
    app_url: Optional[str] = None
    # Processing data
    generic_title: Optional[str] = None
    generic_description: Optional[str] = None
    
    @model_validator(mode="after")
    def _set_app_url(self) -> "MessageRequest":
        if not self.app_url and self.tg_user_id:
            self.app_url = f"tg://user?id={self.tg_user_id}"
        return self


