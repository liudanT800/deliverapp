from datetime import datetime
from typing import Optional
from pydantic import Field
from app.schemas.base import CamelModel

class AppealBase(CamelModel):
    task_id: int
    reason: str

class AppealCreate(AppealBase):
    pass

class AppealHandle(CamelModel):
    status: str  # 'processing', 'resolved', 'rejected'
    admin_reply: str

class AppealRead(AppealBase):
    id: int
    creator_id: int
    status: str
    admin_reply: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
