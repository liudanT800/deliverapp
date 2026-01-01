from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.models.user import User
from app.schemas.chat import MessageCreate, MessageRead, ChatSession
from app.schemas.response import ResponseModel
from app.services.chat_service import chat_service, manager
import json

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/send", response_model=ResponseModel[MessageRead])
async def send_message(
    message_in: MessageCreate,
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
):
    message = await chat_service.send_message(db, message_in, current_user.id)
    
    # 实时广播
    await manager.broadcast_to_task(message_in.task_id, {
        "type": "new_message",
        "data": {
            "id": message.id,
            "taskId": message.task_id,
            "senderId": message.sender_id,
            "receiverId": message.receiver_id,
            "content": message.content,
            "createdAt": message.created_at.isoformat()
        }
    })
    
    return ResponseModel(data=message)

@router.websocket("/ws/{task_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    task_id: int,
    # 注意：WebSocket 认证通常通过 query 参数传递 token，因为 header 支持有限
    token: str | None = None 
):
    # 这里可以添加 token 验证逻辑
    await manager.connect(websocket, task_id)
    try:
        while True:
            # 保持连接，也可以处理客户端发来的心跳或消息
            data = await websocket.receive_text()
            # 如果需要通过 WS 发送消息，可以在这里处理
    except WebSocketDisconnect:
        manager.disconnect(websocket, task_id)

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
