from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.models.user import User
from app.schemas.chat import MessageCreate, MessageRead, ChatSession
from app.schemas.response import ResponseModel
from app.services.chat_service import chat_service

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/send", response_model=ResponseModel[MessageRead])
async def send_message(
    message_in: MessageCreate,
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
):
    message = await chat_service.send_message(db, message_in, current_user.id)
    return ResponseModel(data=message)

@router.get("/history/{task_id}", response_model=ResponseModel[List[MessageRead]])
async def get_history(
    task_id: int,
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
):
    history = await chat_service.get_history(db, task_id)
    return ResponseModel(data=history)

@router.get("/sessions", response_model=ResponseModel[List[ChatSession]])
async def get_sessions(
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
):
    sessions = await chat_service.get_sessions(db, current_user.id)
    return ResponseModel(data=sessions)
