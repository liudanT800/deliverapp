from datetime import datetime
from typing import Optional

from app.schemas.base import CamelModel


class MessageBase(CamelModel):
    task_id: int
    sender_id: int
    receiver_id: int
    content: str
    is_read: bool = False


class MessageCreate(CamelModel):
    task_id: int
    receiver_id: int
    content: str


class MessageRead(MessageBase):
    id: int
    created_at: datetime
    sender: Optional[dict] = None
