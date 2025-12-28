from typing import Annotated
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.task import Task, TaskStatus, TaskCategory, TaskUrgency
from app.models.user import User
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.schemas.response import OperationResponse, ResponseModel
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=ResponseModel[list[TaskRead]])
async def list_tasks(
    keyword: str | None = None,
    status_filter: TaskStatus | None = Query(None, alias="status"),
    min_reward: float | None = None,
    max_reward: float | None = None,
    pickup_location: str | None = None,
    dropoff_location: str | None = None,
    time_range: str | None = None,
    category: TaskCategory | None = None,
    urgency: TaskUrgency | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    session: Annotated[AsyncSession, Depends(deps.get_db)] = None,
):
    stmt = (
        select(Task)
        .options(
            selectinload(Task.created_by),
            selectinload(Task.assigned_to),
        )
    )

    conditions = []
    if keyword:
        like = f"%{keyword}%"
        conditions.append(
            or_(Task.title.ilike(like), Task.description.ilike(like))
        )
    if status_filter:
        conditions.append(Task.status == status_filter)
    if min_reward is not None:
        conditions.append(Task.reward_amount >= min_reward)
    if max_reward is not None:
        conditions.append(Task.reward_amount <= max_reward)
    # 新增筛选条件
    if pickup_location:
        conditions.append(Task.pickup_location_name.ilike(f"%{pickup_location}%"))
    if dropoff_location:
        conditions.append(Task.dropoff_location_name.ilike(f"%{dropoff_location}%"))
    if time_range:
        # 计算时间范围
        now = datetime.utcnow()
        if time_range == "today":
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_range == "week":
            start_time = now - timedelta(days=now.weekday())
            start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_range == "month":
            start_time = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_time = None
            
        if start_time:
            conditions.append(Task.created_at >= start_time)
    # 新增分类和紧急程度筛选
    if category:
        conditions.append(Task.category == category)
    if urgency:
        conditions.append(Task.urgency == urgency)

    if conditions:
        stmt = stmt.where(and_(*conditions))
    
    # 添加排序
    if sort_by == "reward_amount":
        if sort_order == "asc":
            stmt = stmt.order_by(Task.reward_amount.asc())
        else:
            stmt = stmt.order_by(Task.reward_amount.desc())
    elif sort_by == "created_at":
        if sort_order == "asc":
            stmt = stmt.order_by(Task.created_at.asc())
        else:
            stmt = stmt.order_by(Task.created_at.desc())
    else:
        # 默认按创建时间倒序排列
        stmt = stmt.order_by(Task.created_at.desc())

    result = await session.execute(stmt)
    tasks = result.scalars().all()
    
    return ResponseModel(
        success=True,
        message="任务列表获取成功",
        data=tasks
    )


@router.get("/{task_id}", response_model=ResponseModel[TaskRead])
async def get_task(
    task_id: int,
    session: Annotated[AsyncSession, Depends(deps.get_db)],
):
    stmt = (
        select(Task)
        .where(Task.id == task_id)
        .options(
            selectinload(Task.created_by),
            selectinload(Task.assigned_to),
        )
    )
    result = await session.execute(stmt)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return ResponseModel(
        success=True,
        message="任务详情获取成功",
        data=task
    )


from datetime import datetime, timedelta

@router.post("", response_model=ResponseModel[TaskRead], status_code=201)
async def create_task(
    payload: TaskCreate,
    session: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[User, Depends(deps.get_current_active_user)],
):
    # 如果没有设置抢单截止时间，默认为创建时间后1小时
    task_data = payload.model_dump()
    if task_data.get('grab_expires_at') is None:
        task_data['grab_expires_at'] = datetime.utcnow() + timedelta(hours=1)
    
    task = Task(
        **task_data,
        created_by_id=current_user.id,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    
    return ResponseModel(
        success=True,
        message="任务创建成功",
        data=task
    )


@router.post("/{task_id}/accept", response_model=ResponseModel[TaskRead])
async def accept_task(
    task_id: int,
    session: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[User, Depends(deps.get_current_active_user)],
):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 重新加载用户信息，包含 tasks_taken 和 tasks_created 关系，用于信用服务检查
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

    try:
        task_service.ensure_can_accept(task, user_with_tasks)
    except Exception as e:
        # 捕获所有异常并打印，方便调试
        print(f"Error in ensure_can_accept: {str(e)}")
        import traceback
        traceback.print_exc()
        raise e

    task.assigned_to_id = current_user.id
    task.status = TaskStatus.accepted
    await session.commit()
    await session.refresh(task)
    
    return ResponseModel(
        success=True,
        message="任务接取成功",
        data=task
    )


@router.post("/{task_id}/cancel", response_model=ResponseModel[TaskRead])
async def cancel_task(
    task_id: int,
    session: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[User, Depends(deps.get_current_active_user)],
):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 检查用户是否有权限取消任务
    if current_user.id != task.created_by_id and current_user.id != task.assigned_to_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权取消此任务")

    # 检查任务状态是否允许取消
    if task.status not in [TaskStatus.pending, TaskStatus.accepted, TaskStatus.picked, TaskStatus.delivering, TaskStatus.confirming]:
        raise HTTPException(status_code=400, detail="当前任务状态不允许取消")

    old_status = task.status
    task.status = TaskStatus.cancelled
    
    # 记录取消者信息
    if current_user.id == task.created_by_id:
        task.cancelled_by = "creator"
    elif current_user.id == task.assigned_to_id:
        task.cancelled_by = "assignee"
    
    # 更新信用评分
    task_service.update_credit_on_completion(task)
    
    await session.commit()
    await session.refresh(task)
    
    return ResponseModel(
        success=True,
        message=f"任务已成功取消，原状态为 '{old_status}'",
        data=task
    )


@router.post("/{task_id}/status", response_model=ResponseModel[TaskRead])
async def update_task_status(
    task_id: int,
    payload: TaskUpdate,
    session: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[User, Depends(deps.get_current_active_user)],
):
    task = await session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    task_service.ensure_can_update(task, payload.status, current_user)
    old_status = task.status
    task.status = payload.status
    
    # 记录取消者信息
    if task.status == TaskStatus.cancelled:
        if current_user.id == task.created_by_id:
            task.cancelled_by = "creator"
        elif current_user.id == task.assigned_to_id:
            task.cancelled_by = "assignee"
    
    # 如果任务已完成或已取消，更新信用评分
    if task.status in [TaskStatus.completed, TaskStatus.cancelled]:
        task_service.update_credit_on_completion(task)
    
    await session.commit()
    await session.refresh(task)
    
    return ResponseModel(
        success=True,
        message=f"任务状态从 '{old_status}' 更新为 '{payload.status}' 成功",
        data=task
    )