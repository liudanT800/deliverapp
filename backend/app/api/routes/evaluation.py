from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.models.user import User
from app.schemas.evaluation import EvaluationCreate, EvaluationRead, UserEvaluationSummary
from app.schemas.response import ResponseModel
from app.services.evaluation_service import evaluation_service

router = APIRouter(prefix="/evaluation", tags=["evaluation"])

@router.post("/submit", response_model=ResponseModel[EvaluationRead])
async def submit_evaluation(
    evaluation_in: EvaluationCreate,
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
):
    evaluation = await evaluation_service.submit_evaluation(db, evaluation_in, current_user.id)
    return ResponseModel(data=evaluation)

@router.get("/user/{user_id}", response_model=ResponseModel[UserEvaluationSummary])
async def get_user_evaluations(
    user_id: int,
    db: Annotated[AsyncSession, Depends(deps.get_db)]
):
    summary = await evaluation_service.get_user_evaluations(db, user_id)
    return ResponseModel(data=summary)

@router.get("/task/{task_id}", response_model=ResponseModel[List[EvaluationRead]])
async def get_task_evaluations(
    task_id: int,
    db: Annotated[AsyncSession, Depends(deps.get_db)]
):
    evaluations = await evaluation_service.get_task_evaluations(db, task_id)
    return ResponseModel(data=evaluations)
