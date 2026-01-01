from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from app.models.evaluation import Evaluation
from app.models.user import User
from app.schemas.evaluation import EvaluationCreate, UserEvaluationSummary

class EvaluationService:
    async def submit_evaluation(self, db: AsyncSession, evaluation_in: EvaluationCreate, evaluator_id: int):
        db_evaluation = Evaluation(
            task_id=evaluation_in.task_id,
            evaluator_id=evaluator_id,
            evaluatee_id=evaluation_in.evaluatee_id,
            score=evaluation_in.score,
            comment=evaluation_in.comment
        )
        db.add(db_evaluation)
        await db.commit()
        await db.refresh(db_evaluation)
        
        # Update user's credit score or average rating if needed
        await self.update_user_rating(db, evaluation_in.evaluatee_id)
        
        return db_evaluation

    async def update_user_rating(self, db: AsyncSession, user_id: int):
        stmt = select(func.avg(Evaluation.score)).where(Evaluation.evaluatee_id == user_id)
        result = await db.execute(stmt)
        avg_score = result.scalar()
        
        if avg_score:
            user_stmt = select(User).where(User.id == user_id)
            user_result = await db.execute(user_stmt)
            user = user_result.scalar_one_or_none()
            if user:
                user.credit_score = float(avg_score)
                db.add(user)
                await db.commit()

    async def get_user_evaluations(self, db: AsyncSession, user_id: int):
        stmt = select(Evaluation).where(Evaluation.evaluatee_id == user_id)
        result = await db.execute(stmt)
        evaluations = result.scalars().all()
        
        avg_stmt = select(func.avg(Evaluation.score)).where(Evaluation.evaluatee_id == user_id)
        avg_result = await db.execute(avg_stmt)
        avg_score = avg_result.scalar() or 0.0
        
        return UserEvaluationSummary(
            user_id=user_id,
            average_score=float(avg_score),
            total_evaluations=len(evaluations),
            evaluations=evaluations
        )

    async def get_task_evaluations(self, db: AsyncSession, task_id: int):
        stmt = select(Evaluation).where(Evaluation.task_id == task_id)
        result = await db.execute(stmt)
        return result.scalars().all()

evaluation_service = EvaluationService()
