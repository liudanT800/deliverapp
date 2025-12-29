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
