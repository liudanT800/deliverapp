from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Appeal(Base):
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(20), default="pending")  # 'pending', 'processing', 'resolved', 'rejected'
    admin_reply = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    task = relationship("Task")
    creator = relationship("User")
