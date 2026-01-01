from datetime import datetime
from typing import Optional, List
from pydantic import Field
from app.schemas.base import CamelModel
from app.schemas.user import UserRead

class EvaluationBase(CamelModel):
    task_id: int
    evaluatee_id: int
    score: float = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class EvaluationCreate(EvaluationBase):
    pass

class EvaluationRead(EvaluationBase):
    id: int
    evaluator_id: int
    created_at: datetime
    evaluator: Optional[UserRead] = None

    class Config:
        from_attributes = True

class UserEvaluationSummary(CamelModel):
    user_id: int
    average_score: float
    total_evaluations: int
    evaluations: List[EvaluationRead]
