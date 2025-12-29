"""
智能信用评分服务
基于任务类型、复杂度、行为历史等因素动态计算信用评分
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from app.models.user import User
from app.models.task import Task, TaskStatus, TaskCategory, TaskUrgency


class CreditScoringService:
    """信用评分服务"""

    pass

    def calculate_task_score(self, task: Task, action: str, user_role: str) -> float:
        """
        计算任务相关操作的评分变化

        Args:
            task: 任务对象
            action: 操作类型 ('completed', 'cancelled', 'timeout')
            user_role: 用户角色 ('publisher', 'assignee')

        Returns:
            评分变化值
        """
        base_scores = {
            'task_completed_publisher': 0.1,      # 任务完成 - 发布者奖励
            'task_completed_assignee': 0.2,       # 任务完成 - 接单者奖励
            'task_cancelled_assignee': -0.3,      # 接单者取消任务
            'task_cancelled_publisher': -0.1,     # 发布者取消任务
            'task_timeout': -0.2,                  # 任务超时未完成
        }
        
        return base_scores.get(f'task_{action}_{user_role}', 0.0)

    async def assess_user_reliability(self, user: User) -> Dict[str, any]:
        """
        评估用户可靠性

        Returns:
            包含各种统计信息的字典
        """
        from sqlalchemy import select
        from app.db.session import get_session
        from app.models.task import Task, TaskStatus
        
        # 重新获取用户以确保关系被加载
        async for session in get_session():
            # 获取用户发布的任务数量
            published_result = await session.execute(
                select(Task).where(Task.created_by_id == user.id)
            )
            published_tasks = published_result.scalars().all()
            
            # 获取用户接取的任务数量
            taken_result = await session.execute(
                select(Task).where(Task.assigned_to_id == user.id)
            )
            taken_tasks = taken_result.scalars().all()
            
            break  # 只获取一次会话
        
        # 计算完成率
        published_completed = sum(1 for t in published_tasks if t.status == TaskStatus.completed)
        published_total = len(published_tasks)
        publish_completion_rate = published_completed / published_total if published_total > 0 else 0

        taken_completed = sum(1 for t in taken_tasks if t.status == TaskStatus.completed)
        taken_total = len(taken_tasks)
        take_completion_rate = taken_completed / taken_total if taken_total > 0 else 0

        return {
            'publish_completion_rate': publish_completion_rate,
            'take_completion_rate': take_completion_rate,
            'total_published': published_total,
            'total_taken': taken_total,
            'current_score': user.credit_score,
            'score_trend': self._calculate_score_trend(user),
        }

    def _calculate_score_trend(self, user: User) -> str:
        """
        计算用户评分趋势
        这里可以基于历史数据计算是上升、下降还是稳定
        """
        # 简化实现，实际应该基于历史记录
        if user.credit_score >= 4.0:
            return 'excellent'  # 优秀
        elif user.credit_score >= 3.0:
            return 'good'       # 良好
        elif user.credit_score >= 2.0:
            return 'fair'       # 一般
        else:
            return 'poor'       # 较差

    def can_accept_task(self, user: User, task: Task) -> Dict[str, any]:
        """
        判断用户是否有资格接取任务
        """
        # 基础检查：不能接自己的任务
        if task.created_by_id == user.id:
            return {
                'can_accept': False,
                'reason': '不能接取自己发布的任务',
                'confidence': 1.0
            }
        
        # 检查用户是否已经有太多进行中的任务
        active_tasks_count = sum(
            1 for t in user.tasks_taken
            if t.status not in [TaskStatus.completed, TaskStatus.cancelled]
        )
        
        if active_tasks_count >= 5:  # 简单限制，最多同时进行5个任务
            return {
                'can_accept': False,
                'reason': f'同时进行的任务过多 (最多 5 个)',
                'confidence': 0.8
            }
        
        return {
            'can_accept': True,
            'reason': '符合接单条件',
            'confidence': 0.95
        }




# 全局服务实例
credit_service = CreditScoringService()
