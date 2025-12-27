from fastapi import HTTPException, status

from app.models.user import User
from app.models.task import Task, TaskStatus
from app.services.credit_service import credit_service


def update_credit_score(user: User, delta: float) -> None:
    """
    更新用户信用评分
    
    Args:
        user: 要更新的用户
        delta: 信用分变化值，正数表示增加，负数表示减少
    """
    new_score = user.credit_score + delta
    
    # 信用分范围控制在0-5之间
    if new_score > 5.0:
        new_score = 5.0
    elif new_score < 0.0:
        new_score = 0.0
        
    user.credit_score = new_score


def can_accept_task(user: User, task: Task) -> bool:
    """
    检查用户是否有资格接取任务（使用智能信用评分系统）

    Args:
        user: 用户
        task: 任务

    Returns:
        bool: 是否有资格接取
    """
    result = credit_service.can_accept_task(user, task)
    return result['can_accept']