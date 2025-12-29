from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    campus = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="student")
    verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    credit_score = Column(Float, default=3.5)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    tasks_created = relationship(
        "Task",
        back_populates="created_by",
        foreign_keys="Task.created_by_id",
    )
    tasks_taken = relationship(
        "Task",
        back_populates="assigned_to",
        foreign_keys="Task.assigned_to_id",
    )

