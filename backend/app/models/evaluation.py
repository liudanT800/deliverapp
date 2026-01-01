from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, Float
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Evaluation(Base):
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id", ondelete="CASCADE"), nullable=False)
    evaluator_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    evaluatee_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    score = Column(Float, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    task = relationship("Task")
    evaluator = relationship("User", foreign_keys=[evaluator_id])
    evaluatee = relationship("User", foreign_keys=[evaluatee_id])
