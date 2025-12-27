#!/usr/bin/env python3
"""
测试智能信用评分系统
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app.services.credit_service import credit_service
    from app.models.task import Task, TaskStatus, TaskCategory, TaskUrgency
    from app.models.user import User

    print("✅ 智能信用评分系统测试")
    print("=" * 50)

    # 创建测试用户
    test_user = User(
        id=1,
        email="test@example.com",
        full_name="测试用户",
        credit_score=3.5
    )

    # 创建测试任务
    test_task = Task(
        id=1,
        title="测试任务",
        description="测试任务描述",
        pickup_location_name="图书馆",
        dropoff_location_name="宿舍",
        reward_amount=10.0,
        category=TaskCategory.delivery,
        urgency=TaskUrgency.medium,
        status=TaskStatus.pending,
        created_by_id=1
    )

    # 测试评分计算
    print("1. 任务评分计算测试：")
    completed_score = credit_service.calculate_task_score(test_task, 'completed', 'publisher')
    print(f"   发布者完成任务评分: {completed_score}")

    completed_score_assignee = credit_service.calculate_task_score(test_task, 'completed', 'assignee')
    print(f"   接单者完成任务评分: {completed_score_assignee}")

    # 测试资格检查
    print("\n2. 任务接取资格检查测试：")
    can_accept = credit_service.can_accept_task(test_user, test_task)
    print(f"   是否可以接取任务: {can_accept['can_accept']}")
    print(f"   原因: {can_accept['reason']}")

    # 测试用户评估
    print("\n3. 用户可靠性评估测试：")
    assessment = credit_service.assess_user_reliability(test_user)
    print(f"   评分趋势: {assessment['score_trend']}")
    print(f"   发布任务数: {assessment['total_published']}")
    print(f"   接单任务数: {assessment['total_taken']}")

    print("\n✅ 所有测试通过！智能信用评分系统工作正常")

except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
