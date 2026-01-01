from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.models.user import User
from app.schemas.payment import WalletRead, RechargeRequest, TransactionRead, PaymentRequest
from app.schemas.response import ResponseModel, OperationResponse
from app.services.payment_service import payment_service

router = APIRouter(prefix="/payment", tags=["payment"])

@router.get("/balance", response_model=ResponseModel[WalletRead])
async def get_balance(
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
):
    wallet = await payment_service.get_balance(db, current_user.id)
    return ResponseModel(data=wallet)

@router.post("/recharge", response_model=ResponseModel[WalletRead])
async def recharge(
    recharge_in: RechargeRequest,
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
):
    wallet = await payment_service.recharge(db, current_user.id, recharge_in)
    return ResponseModel(data=wallet)

@router.get("/transactions", response_model=ResponseModel[List[TransactionRead]])
async def get_transactions(
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
):
    transactions = await payment_service.get_transactions(db, current_user.id)
    return ResponseModel(data=transactions)

@router.post("/pay", response_model=OperationResponse)
async def pay_reward(
    payment_in: PaymentRequest,
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
):
    success = await payment_service.pay_reward(db, current_user.id, payment_in.task_id, payment_in.amount)
    return OperationResponse(success=success, message="支付成功" if success else "支付失败")

@router.post("/settle", response_model=OperationResponse)
async def settle_reward(
    payment_in: PaymentRequest,
    current_user: Annotated[User, Depends(deps.get_current_user)],
    db: Annotated[AsyncSession, Depends(deps.get_db)]
):
    # In a real app, this would be restricted to admin or triggered by task completion
    success = await payment_service.settle_reward(db, current_user.id, payment_in.task_id, payment_in.amount)
    return OperationResponse(success=success, message="结算成功" if success else "结算失败")
