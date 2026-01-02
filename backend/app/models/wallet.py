from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Float

from app.db.base_class import Base


class Wallet(Base):
    __tablename__ = "wallet"

    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    balance = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
