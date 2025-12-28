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

    # 基础评分配置
    BASE_SCORES = {
        'task_completed_publisher': 0.1,      # 任务完成 - 发布者奖励
        'task_completed_assignee': 0.2,       # 任务完成 - 接单者奖励
        'task_cancelled_assignee': -0.3,      # 接单者取消任务
        'task_cancelled_publisher': -0.1,     # 发布者取消任务
        'task_timeout': -0.2,                  # 任务超时未完成
    }

    # 任务类型系数（根据任务复杂度调整评分）
    CATEGORY_MULTIPLIERS = {
        TaskCategory.delivery: 1.0,    # 快递代取 - 标准难度
        TaskCategory.food: 0.8,        # 餐饮代买 - 较低难度
        TaskCategory.document: 1.2,    # 文件传递 - 较高要求
        TaskCategory.purchase: 1.1,    # 物品代购 - 中等难度
        TaskCategory.other: 1.0,       # 其他 - 标准难度
    }

    # 紧急程度系数
    URGENCY_MULTIPLIERS = {
        TaskUrgency.low: 0.9,          # 一般 - 降低评分
        TaskUrgency.medium: 1.0,       # 较急 - 标准评分
        TaskUrgency.high: 1.3,         # 紧急 - 提高评分
    }

    # 任务价值系数（基于酬金）
    REWARD_MULTIPLIERS = {
        (0, 5): 0.8,      # 0-5元：低价值任务
        (5, 10): 1.0,     # 5-10元：标准价值
        (10, 20): 1.2,    # 10-20元：较高价值
        (20, float('inf')): 1.5,  # 20元以上：高价值任务
    }

    def __init__(self):
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
        base_key = f'task_{action}_{user_role}'
        base_score = self.BASE_SCORES.get(base_key, 0.0)

        if base_score == 0.0:
            return 0.0

        # 计算各种系数
        category_multiplier = self.CATEGORY_MULTIPLIERS.get(task.category, 1.0)
        urgency_multiplier = self.URGENCY_MULTIPLIERS.get(task.urgency, 1.0)
        reward_multiplier = self._get_reward_multiplier(task.reward_amount)

        # 最终评分 = 基础分 × 类别系数 × 紧急系数 × 价值系数
        final_score = base_score * category_multiplier * urgency_multiplier * reward_multiplier

        # 保留两位小数
        return round(final_score, 2)

    def _get_reward_multiplier(self, reward_amount: float) -> float:
        """根据任务酬金获取价值系数"""
        for (min_val, max_val), multiplier in self.REWARD_MULTIPLIERS.items():
            if min_val <= reward_amount < max_val:
                return multiplier
        return 1.0

    def assess_user_reliability(self, user: User) -> Dict[str, any]:
        """
        评估用户可靠性

        Returns:
            包含各种统计信息的字典
        """
        # 获取用户的所有任务
        # 注意：这里假设 user 对象已经预加载了 tasks_created 和 tasks_taken
        # 如果没有预加载，这里会返回空列表或报错，取决于 SQLAlchemy 配置
        published_tasks = getattr(user, 'tasks_created', [])
        taken_tasks = getattr(user, 'tasks_taken', [])

        # 计算完成率
        published_completed = sum(1 for t in published_tasks if t.status == TaskStatus.completed)
        published_total = len(published_tasks)
        publish_completion_rate = published_completed / published_total if published_total > 0 else 0

        taken_completed = sum(1 for t in taken_tasks if t.status == TaskStatus.completed)
        taken_total = len(taken_tasks)
        take_completion_rate = taken_completed / taken_total if taken_total > 0 else 0

        # 计算平均评分变化
        credit_changes = []
        for task in published_tasks + taken_tasks:
            if task.status in [TaskStatus.completed, TaskStatus.cancelled]:
                # 这里需要实现获取该任务对用户的评分变化历史
                pass

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
        智能判断用户是否有资格接取任务

        Returns:
            {
                'can_accept': bool,
                'reason': str,  # 如果不能接受的原因
                'confidence': float  # 置信度 0-1
            }
        """
        # 基础检查：不能接自己的任务
        if task.created_by_id == user.id:
            return {
                'can_accept': False,
                'reason': '不能接取自己发布的任务',
                'confidence': 1.0
            }

        # 信用分检查
        min_score = self._get_dynamic_min_score(user, task)
        if user.credit_score < min_score:
            return {
                'can_accept': False,
                'reason': f'信用分不足 (需要 {min_score}, 当前 {user.credit_score})',
                'confidence': 0.9
            }

        # 活跃任务数量检查
        max_active_tasks = self._get_max_active_tasks(user)
        
        # 安全获取 tasks_taken
        tasks_taken = getattr(user, 'tasks_taken', [])
        
        active_tasks_count = sum(
            1 for t in tasks_taken
            if t.status not in [TaskStatus.completed, TaskStatus.cancelled]
        )

        if active_tasks_count >= max_active_tasks:
            return {
                'can_accept': False,
                'reason': f'同时进行的任务过多 (最多 {max_active_tasks} 个)',
                'confidence': 0.8
            }

        # 行为模式检查
        behavior_check = self._check_behavior_pattern(user, task)
        if not behavior_check['passed']:
            return {
                'can_accept': False,
                'reason': behavior_check['reason'],
                'confidence': behavior_check['confidence']
            }

        return {
            'can_accept': True,
            'reason': '符合接单条件',
            'confidence': 0.95
        }

    def _get_dynamic_min_score(self, user: User, task: Task) -> float:
        """
        根据用户历史和任务类型动态计算最低信用分要求
        """
        base_min_score = 2.0  # 基础最低分

        # 根据任务价值调整要求
        if task.reward_amount >= 20:
            base_min_score += 0.5  # 高价值任务要求更高信用
        elif task.reward_amount >= 10:
            base_min_score += 0.2

        # 根据紧急程度调整
        if task.urgency == TaskUrgency.high:
            base_min_score += 0.3

        # 根据用户历史调整
        user_reliability = self.assess_user_reliability(user)
        if user_reliability['score_trend'] == 'poor':
            base_min_score += 0.5  # 表现不好的用户要求更高

        return min(base_min_score, 4.0)  # 最高不超过4.0

    def _get_max_active_tasks(self, user: User) -> int:
        """
        根据用户信用分动态确定最大同时进行的任务数量
        """
        if user.credit_score >= 4.5:
            return 8  # 高信用用户可以接更多任务
        elif user.credit_score >= 4.0:
            return 6
        elif user.credit_score >= 3.0:
            return 5
        elif user.credit_score >= 2.5:
            return 4
        else:
            return 3  # 低信用用户限制更严格

    def _check_behavior_pattern(self, user: User, task: Task) -> Dict[str, any]:
        """
        检查用户行为模式，防止滥用系统
        """
        # 安全获取 tasks_taken
        tasks_taken = getattr(user, 'tasks_taken', [])
        
        # 检查近期取消率
        recent_tasks = [t for t in tasks_taken
                       if (datetime.utcnow() - t.created_at).days <= 30]

        if len(recent_tasks) >= 5:
            cancelled_count = sum(1 for t in recent_tasks if t.status == TaskStatus.cancelled)
            cancel_rate = cancelled_count / len(recent_tasks)

            if cancel_rate > 0.3:  # 30% 取消率
                return {
                    'passed': False,
                    'reason': '近期取消任务过多，请提高完成率',
                    'confidence': 0.7
                }

        return {
            'passed': True,
            'reason': '行为模式正常',
            'confidence': 0.9
        }


# 全局服务实例
credit_service = CreditScoringService()
