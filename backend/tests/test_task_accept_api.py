import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.security import get_password_hash
from app.models.task import Task, TaskStatus

@pytest.mark.anyio
async def test_accept_task_flow(client: AsyncClient, db_session: AsyncSession):
    # 1. 创建两个测试用户
    unique_id = str(uuid.uuid4())[:8]
    # 用户 A: 发布者
    user_a_data = {
        "email": f"publisher_{unique_id}@example.com",
        "password": "password123",
        "full_name": "Publisher User",
        "phone": "13800138001",
        "campus": "Campus A"
    }
    # 用户 B: 接单者
    user_b_data = {
        "email": f"acceptor_{unique_id}@example.com",
        "password": "password123",
        "full_name": "Acceptor User",
        "phone": "13800138002",
        "campus": "Campus B"
    }

    # 注册用户 A
    resp_a = await client.post("/api/auth/register", json=user_a_data)
    if resp_a.status_code != 201:
        print(f"Register A failed: {resp_a.text}")
    assert resp_a.status_code == 201
    
    # 注册用户 B
    resp_b = await client.post("/api/auth/register", json=user_b_data)
    assert resp_b.status_code == 201
    
    # 登录用户 A 获取 token
    login_a = await client.post("/api/auth/login", json={
        "email": user_a_data["email"],
        "password": user_a_data["password"]
    })
    token_a = login_a.json()["data"]["accessToken"]
    
    # 登录用户 B 获取 token
    login_b = await client.post("/api/auth/login", json={
        "email": user_b_data["email"],
        "password": user_b_data["password"]
    })
    token_b = login_b.json()["data"]["accessToken"]
    
    # 2. 用户 A 发布任务
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "pickupLocationName": "Location A",
        "dropoffLocationName": "Location B",
        "rewardAmount": 10.0,
        "category": "delivery",
        "urgency": "medium"
    }
    resp_task = await client.post(
        "/api/tasks", 
        json=task_data,
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert resp_task.status_code == 201
    task_id = resp_task.json()["data"]["id"]
    
    # 3. 用户 B 接单
    print(f"\nTesting accept task {task_id} with user B...")
    resp_accept = await client.post(
        f"/api/tasks/{task_id}/accept",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    
    # 打印详细错误信息如果失败
    if resp_accept.status_code != 200:
        print(f"Accept failed with status {resp_accept.status_code}")
        print(f"Response: {resp_accept.text}")
    
    assert resp_accept.status_code == 200
    assert resp_accept.json()["success"] is True
    assert resp_accept.json()["data"]["status"] == "accepted"
    assert resp_accept.json()["data"]["assignedTo"]["id"] is not None
    assert resp_accept.json()["data"]["createdBy"]["id"] is not None
    print("Accept task test passed with full relationship check!")

    # 4. 测试不能接取自己发布的任务
    task_data_2 = {
        "title": "Task by B",
        "description": "Description",
        "pickupLocationName": "Loc A",
        "dropoffLocationName": "Loc B",
        "rewardAmount": 5.0,
        "category": "delivery"
    }
    resp_task_2 = await client.post(
        "/api/tasks", 
        json=task_data_2,
        headers={"Authorization": f"Bearer {token_b}"}
    )
    task_id_2 = resp_task_2.json()["data"]["id"]
    
    resp_accept_self = await client.post(
        f"/api/tasks/{task_id_2}/accept",
        headers={"Authorization": f"Bearer {token_b}"}
    )
    assert resp_accept_self.status_code == 400
    assert "不能接取自己发布的任务" in resp_accept_self.json()["message"]
    print("Self-accept prevention test passed!")

    # 5. 测试不能接取已接取的任务
    resp_accept_again = await client.post(
        f"/api/tasks/{task_id}/accept",
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert resp_accept_again.status_code == 400
    assert "任务不可接单" in resp_accept_again.json()["message"]
    print("Already accepted prevention test passed!")
