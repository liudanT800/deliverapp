from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from app.models.payment import Wallet, Transaction
from app.models.task import Task
from app.schemas.payment import RechargeRequest

class PaymentService:
    async def get_balance(self, db: AsyncSession, user_id: int):
        stmt = select(Wallet).where(Wallet.user_id == user_id)
        result = await db.execute(stmt)
        wallet = result.scalar_one_or_none()
        if not wallet:
            wallet = Wallet(user_id=user_id, balance=0.0)
            db.add(wallet)
            await db.commit()
            await db.refresh(wallet)
        return wallet

    async def recharge(self, db: AsyncSession, user_id: int, recharge_in: RechargeRequest):
        wallet = await self.get_balance(db, user_id)
        wallet.balance += recharge_in.amount
        
        transaction = Transaction(
            user_id=user_id,
            amount=recharge_in.amount,
            type='deposit',
            description='账户充值'
        )
        db.add(transaction)
        await db.commit()
        await db.refresh(wallet)
        return wallet

    async def get_transactions(self, db: AsyncSession, user_id: int):
        stmt = select(Transaction).where(Transaction.user_id == user_id).order_by(Transaction.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()

    async def pay_reward(self, db: AsyncSession, user_id: int, task_id: int, amount: float):
        wallet = await self.get_balance(db, user_id)
        if wallet.balance < amount:
            raise HTTPException(status_code=400, detail="余额不足")
        
        wallet.balance -= amount
        transaction = Transaction(
            user_id=user_id,
            amount=-amount,
            type='payment',
            related_id=task_id,
            description=f'支付任务赏金: 任务#{task_id}'
        )
        db.add(transaction)
        await db.commit()
        return True

    async def settle_reward(self, db: AsyncSession, user_id: int, task_id: int, amount: float):
        wallet = await self.get_balance(db, user_id)
        wallet.balance += amount
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            type='reward',
            related_id=task_id,
            description=f'获得任务赏金: 任务#{task_id}'
        )
        db.add(transaction)
        await db.commit()
        return True

payment_service = PaymentService()
