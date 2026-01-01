from datetime import datetime
from typing import Optional
from pydantic import Field
from app.schemas.base import CamelModel
from app.schemas.user import UserRead

class MessageBase(CamelModel):
    task_id: int
    content: str

class MessageCreate(MessageBase):
    receiver_id: int

class MessageRead(MessageBase):
    id: int
    sender_id: int
    receiver_id: int
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ChatSession(CamelModel):
    task_id: int
    other_user: UserRead
    last_message: Optional[str]
    last_message_time: Optional[datetime]
    unread_count: int
