from pydantic import BaseModel, Field
from typing import Optional

class FromTG(BaseModel):
    chat_id: int = Field(alias='id') 
    is_bot: bool 
    first_name: str 
    last_name: str = None
    username: str = None
    language_code: str 


class FromTGBot(BaseModel):
    chat_id: int = Field(alias='id') 
    is_bot: bool 
    first_name: str 
    username: str = None
   


class ReplyMessage(BaseModel):
    message_id: int = None
    from_tg: FromTGBot = Field(alias='from')
    chat: dict = None
    date: int = None
    text: str = None


class BotMessage(BaseModel):
    message_id: Optional[int] = None
    from_tg: FromTG = Field(alias='from')
    chat: Optional[dict] = None
    date: Optional[int] = None
    text: Optional[str] = None
    reply_to_message: Optional[ReplyMessage] = None


class BotUpdateModel(BaseModel):
    update_id: Optional[int]
    message:BotMessage = None


class ReplyKeyboardMarkup(BaseModel):
    keyboard: list


class KeyboardButton(BaseModel):
    text: str
