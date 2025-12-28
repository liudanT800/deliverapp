from fastapi import HTTPException, status

from app.models.user import User
from app.models.task import Task, TaskStatus



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
    检查用户是否有资格接取任务

    Args:
        user: 用户
        task: 任务

    Returns:
        bool: 是否有资格接取
    """
    # 基础检查：不能接自己的任务
    if task.created_by_id == user.id:
        return False
    
    # 检查用户是否已经有太多进行中的任务
    active_tasks_count = sum(
        1 for t in user.tasks_taken
        if t.status not in [TaskStatus.completed, TaskStatus.cancelled]
    )
    
    # 简单限制，最多同时进行5个任务
    return active_tasks_count < 5