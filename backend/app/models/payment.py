from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Wallet(Base):
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    balance = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", backref="wallet", uselist=False)

class Transaction(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String(20), nullable=False)  # 'deposit', 'withdraw', 'payment', 'reward'
    related_id = Column(Integer, nullable=True)  # 关联的任务ID或其他业务ID
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User")
