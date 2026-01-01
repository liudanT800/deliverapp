from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.appeal import Appeal
from app.schemas.appeal import AppealCreate, AppealHandle

class AppealService:
    async def create_appeal(self, db: AsyncSession, appeal_in: AppealCreate, creator_id: int):
        db_appeal = Appeal(
            task_id=appeal_in.task_id,
            creator_id=creator_id,
            reason=appeal_in.reason
        )
        db.add(db_appeal)
        await db.commit()
        await db.refresh(db_appeal)
        return db_appeal

    async def get_my_appeals(self, db: AsyncSession, user_id: int):
        stmt = select(Appeal).where(Appeal.creator_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_appeal_detail(self, db: AsyncSession, appeal_id: int):
        stmt = select(Appeal).where(Appeal.id == appeal_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def handle_appeal(self, db: AsyncSession, appeal_id: int, handle_in: AppealHandle):
        db_appeal = await self.get_appeal_detail(db, appeal_id)
        if db_appeal:
            db_appeal.status = handle_in.status
            db_appeal.admin_reply = handle_in.admin_reply
            await db.commit()
            await db.refresh(db_appeal)
        return db_appeal

appeal_service = AppealService()
