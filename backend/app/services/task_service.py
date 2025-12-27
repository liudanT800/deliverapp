from collections import defaultdict
from datetime import datetime

from fastapi import HTTPException, status

from app.models.task import Task, TaskStatus
from app.models.user import User
from app.services.user_service import update_credit_score
from app.services.credit_service import credit_service

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
    
    # 使用智能信用服务检查是否有资格接取任务
    accept_check = credit_service.can_accept_task(user, task)
    if not accept_check['can_accept']:
        raise HTTPException(status_code=400, detail=accept_check['reason'])


def ensure_can_update(task: Task, target_status: TaskStatus, user: User) -> None:
    if task.created_by_id != user.id and task.assigned_to_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权更新任务状态")

    allowed = ALLOWED_TRANSITIONS.get(task.status, set())
    if target_status not in allowed:
        raise HTTPException(status_code=400, detail="非法的状态流转")


def update_credit_on_completion(task: Task) -> None:
    """
    任务完成后更新双方信用评分（智能评分系统）
    """
    creator = task.created_by
    assignee = task.assigned_to

    # 任务正常完成，双方都加分
    if task.status == TaskStatus.completed:
        # 发布者奖励
        creator_score = credit_service.calculate_task_score(task, 'completed', 'publisher')
        update_credit_score(creator, creator_score)

        # 接单者奖励
        if assignee:
            assignee_score = credit_service.calculate_task_score(task, 'completed', 'assignee')
            update_credit_score(assignee, assignee_score)

    # 任务被取消，根据情况扣分
    elif task.status == TaskStatus.cancelled:
        # 如果是接单者取消，扣分
        if assignee and task.cancelled_by == 'assignee':
            cancel_score = credit_service.calculate_task_score(task, 'cancelled', 'assignee')
            update_credit_score(assignee, cancel_score)
        # 如果是发布者取消，轻微扣分
        elif task.cancelled_by == 'creator':
            cancel_score = credit_service.calculate_task_score(task, 'cancelled', 'publisher')
            update_credit_score(creator, cancel_score)

