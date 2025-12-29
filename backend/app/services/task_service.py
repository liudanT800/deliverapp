from collections import defaultdict
from datetime import datetime
from typing import Dict, Optional

from fastapi import HTTPException, status

from app.models.task import Task, TaskStatus
from app.models.user import User
from app.services.user_service import update_credit_score

from app.utils.map_service import amap_service

ALLOWED_TRANSITIONS = {
    TaskStatus.pending: {TaskStatus.accepted, TaskStatus.cancelled},
    TaskStatus.accepted: {TaskStatus.picked, TaskStatus.cancelled},
    TaskStatus.picked: {TaskStatus.delivering},
    TaskStatus.delivering: {TaskStatus.confirming},
    TaskStatus.confirming: {TaskStatus.completed, TaskStatus.cancelled},
}


def ensure_can_accept(task: Task, user: User) -> None:
    if task.status != TaskStatus.pending:
        raise HTTPException(status_code=400, detail="任务不可接单")
    
    # 检查是否在抢单有效期内
    if task.grab_expires_at and datetime.utcnow() > task.grab_expires_at:
        raise HTTPException(status_code=400, detail="抢单时间已过，无法接取任务")
    
    # 检查用户是否有资格接取任务
    from app.services.credit_service import credit_service
    result = credit_service.can_accept_task(user, task)
    if not result['can_accept']:
        raise HTTPException(status_code=400, detail=result['reason'])


def ensure_can_update(task: Task, target_status: TaskStatus, user: User) -> None:
    if task.created_by_id != user.id and task.assigned_to_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权更新任务状态")

    allowed = ALLOWED_TRANSITIONS.get(task.status, set())
    if target_status not in allowed:
        raise HTTPException(status_code=400, detail="非法的状态流转")


async def geocode_location(address: str) -> Optional[Dict]:
    """
    将地址转换为经纬度坐标
    
    Args:
        address: 地址字符串
        
    Returns:
        包含坐标信息的字典
    """
    return await amap_service.geocode(address)


async def calculate_task_distance(task: Task) -> Optional[Dict]:
    """
    计算任务起点到终点的距离和时间
    
    Args:
        task: 任务对象
        
    Returns:
        包含距离和时间信息的字典
    """
    if task.pickup_lat and task.pickup_lng and task.dropoff_lat and task.dropoff_lng:
        origins = [(task.pickup_lng, task.pickup_lat)]
        destinations = [(task.dropoff_lng, task.dropoff_lat)]
        
        return await amap_service.get_distance(origins, destinations)
    
    return None


def update_credit_on_completion(task: Task) -> None:
    """
    任务完成后更新双方信用评分（智能评分系统）
    """
    creator = task.created_by
    assignee = task.assigned_to

    # 任务正常完成，双方都加分
    if task.status == TaskStatus.completed:
        # 发布者奖励
        update_credit_score(creator, 0.1)

        # 接单者奖励
        if assignee:
            update_credit_score(assignee, 0.2)

    # 任务被取消，根据情况扣分
    elif task.status == TaskStatus.cancelled:
        # 如果是接单者取消，扣分
        if assignee and task.cancelled_by == 'assignee':
            update_credit_score(assignee, -0.3)
        # 如果是发布者取消，轻微扣分
        elif task.cancelled_by == 'creator':
            update_credit_score(creator, -0.1)

