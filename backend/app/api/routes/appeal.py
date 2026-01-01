from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.models.user import User
from app.schemas.appeal import AppealCreate, AppealRead, AppealHandle
from app.schemas.response import ResponseModel
from app.services.appeal_service import appeal_service

router = APIRouter(prefix="/appeal", tags=["appeal"])

@router.post("/create", response_model=ResponseModel[AppealRead])
async def create_appeal(
    appeal_in: AppealCreate,
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
):
    appeal = await appeal_service.create_appeal(db, appeal_in, current_user.id)
    return ResponseModel(data=appeal)

@router.get("/my", response_model=ResponseModel[List[AppealRead]])
async def get_my_appeals(
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
):
    appeals = await appeal_service.get_my_appeals(db, current_user.id)
    return ResponseModel(data=appeals)

@router.get("/{appeal_id}", response_model=ResponseModel[AppealRead])
async def get_appeal_detail(
    appeal_id: int,
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
):
    appeal = await appeal_service.get_appeal_detail(db, appeal_id)
    if not appeal:
        raise HTTPException(status_code=404, detail="申诉不存在")
    return ResponseModel(data=appeal)

@router.put("/{appeal_id}/handle", response_model=ResponseModel[AppealRead])
async def handle_appeal(
    appeal_id: int,
    handle_in: AppealHandle,
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
):
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可处理申诉")
    
    appeal = await appeal_service.handle_appeal(db, appeal_id, handle_in)
    if not appeal:
        raise HTTPException(status_code=404, detail="申诉不存在")
    return ResponseModel(data=appeal)
