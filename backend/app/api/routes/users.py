from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.api import deps
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate
from app.schemas.response import ResponseModel
from app.services.credit_service import credit_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=ResponseModel[UserRead])
async def read_current_user(
    request: Request,
    current_user: User = Depends(deps.get_current_active_user)
):
    logger.info(f"获取当前用户信息: {current_user.email}")
    request_id = getattr(request.state, 'request_id', None)
    return ResponseModel(
        success=True,
        message="用户信息获取成功",
        data=current_user,
        request_id=request_id
    )


@router.put("/me", response_model=ResponseModel[UserRead])
async def update_current_user(
    request: Request,
    payload: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user),
    session = Depends(deps.get_db),
):
    # 更新用户信息
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    await session.commit()
    await session.refresh(current_user)

    request_id = getattr(request.state, 'request_id', None)
    return ResponseModel(
        success=True,
        message="用户信息更新成功",
        data=current_user,
        request_id=request_id
    )


@router.get("/me/credit", response_model=ResponseModel[dict])
async def get_credit_info(
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
    session: AsyncSession = Depends(deps.get_db),
):
    """获取用户的信用评分详情"""
    # 重新加载用户信息，包含 tasks_taken 和 tasks_created 关系
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    
    stmt = (
        select(User)
        .where(User.id == current_user.id)
        .options(
            selectinload(User.tasks_taken),
            selectinload(User.tasks_created)
        )
    )
    result = await session.execute(stmt)
    user_with_tasks = result.scalar_one()
    
    credit_info = await credit_service.assess_user_reliability(user_with_tasks)

    request_id = getattr(request.state, 'request_id', None)
    return ResponseModel(
        success=True,
        message="信用信息获取成功",
        data={
            "current_score": user_with_tasks.credit_score,
            "score_trend": credit_info['score_trend'],
            "completion_rates": {
                "publish": credit_info['publish_completion_rate'],
                "take": credit_info['take_completion_rate']
            },
            "task_counts": {
                "published": credit_info['total_published'],
                "taken": credit_info['total_taken']
            },
            "next_level_requirements": _get_next_level_requirements(user_with_tasks.credit_score)
        },
        request_id=request_id
    )


def _get_next_level_requirements(current_score: float) -> dict:
    """获取升级到下一级所需的要求"""
    levels = [
        (2.0, "入门级", "完成基础任务"),
        (3.0, "普通级", "保持良好完成率"),
        (4.0, "优秀级", "高完成率和好评"),
        (4.5, "专家级", "长期优秀表现"),
        (5.0, "大师级", "系统内顶尖用户")
    ]

    for threshold, level_name, description in levels:
        if current_score < threshold:
            return {
                "next_level": level_name,
                "required_score": threshold,
                "remaining_score": round(threshold - current_score, 2),
                "description": description
            }

    return {
        "next_level": "已达最高级",
        "required_score": 5.0,
        "remaining_score": 0,
        "description": "恭喜您已成为大师级用户！"
    }