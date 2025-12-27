from datetime import datetime
from typing import Optional

from pydantic import Field

from app.models.task import TaskStatus, TaskCategory, TaskUrgency
from app.schemas.base import CamelModel
from app.schemas.user import UserRead


class TaskBase(CamelModel):
    title: str = Field(..., max_length=120)
    description: str
    pickup_location_name: str
    dropoff_location_name: str
    reward_amount: float = Field(..., ge=1)
    pickup_lat: Optional[float] = None
    pickup_lng: Optional[float] = None
    dropoff_lat: Optional[float] = None
    dropoff_lng: Optional[float] = None
    expires_at: Optional[datetime] = None
    grab_expires_at: Optional[datetime] = None  # 抢单截止时间
    # 新增字段
    category: Optional[TaskCategory] = None
    urgency: TaskUrgency = TaskUrgency.medium


class TaskCreate(TaskBase):
    pass


class TaskUpdate(CamelModel):
    status: TaskStatus


class TaskRead(TaskBase):
    id: int
    status: TaskStatus
    cancelled_by: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    created_by: UserRead | None = None
    assigned_to: UserRead | None = None