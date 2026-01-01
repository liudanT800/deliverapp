from datetime import datetime
from typing import Optional
from pydantic import Field
from app.schemas.base import CamelModel

class WalletRead(CamelModel):
    user_id: int
    balance: float
    updated_at: datetime

    class Config:
        from_attributes = True

class RechargeRequest(CamelModel):
    amount: float = Field(..., ge=0.01)

class TransactionRead(CamelModel):
    id: int
    user_id: int
    amount: float
    type: str
    related_id: Optional[int] = None
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PaymentRequest(CamelModel):
    task_id: int
    amount: float
