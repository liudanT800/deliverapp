from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, DateTime, Enum as SQLEnum, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class TaskStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    picked = "picked"
    delivering = "delivering"
    confirming = "confirming"
    completed = "completed"
    cancelled = "cancelled"


class TaskCategory(str, Enum):
    delivery = "delivery"
    food = "food"
    document = "document"
    purchase = "purchase"
    other = "other"


class TaskUrgency(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Task(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    reward_amount: Mapped[float] = mapped_column(Float(asdecimal=False), nullable=False)
    
    # 新增字段
    category: Mapped[TaskCategory] = mapped_column(SQLEnum(TaskCategory), nullable=True)
    urgency: Mapped[TaskUrgency] = mapped_column(SQLEnum(TaskUrgency), default=TaskUrgency.medium)

    pickup_location_name: Mapped[str] = mapped_column(String(120), nullable=False)
    pickup_lat: Mapped[Optional[float]] = mapped_column(nullable=True)
    pickup_lng: Mapped[Optional[float]] = mapped_column(nullable=True)

    dropoff_location_name: Mapped[str] = mapped_column(String(120), nullable=False)
    dropoff_lat: Mapped[Optional[float]] = mapped_column(nullable=True)
    dropoff_lng: Mapped[Optional[float]] = mapped_column(nullable=True)

    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus), default=TaskStatus.pending, index=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    grab_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)  # 抢单截止时间
    cancelled_by: Mapped[str | None] = mapped_column(String(20), nullable=True)  # 取消者类型: 'creator' 或 'assignee'
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 添加索引以提高查询性能
    __table_args__ = (
        Index('ix_task_status_created_at', 'status', 'created_at'),
        Index('ix_task_grab_expires_at', 'grab_expires_at'),
    )

    created_by_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    assigned_to_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )

    created_by = relationship(
        "User",
        foreign_keys=[created_by_id],
        back_populates="tasks_created",
    )
    assigned_to = relationship(
        "User",
        foreign_keys=[assigned_to_id],
        back_populates="tasks_taken",
    )