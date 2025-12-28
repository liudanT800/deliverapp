import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_register_user(client: AsyncClient):
    # 准备注册数据
    payload = {
        "email": "test_register@example.com",
        "password": "strongpassword123",
        "full_name": "Test User",
        "phone": "13800000000",
        "campus": "Test Campus"
    }

    # 发送注册请求
    response = await client.post("/api/auth/register", json=payload)

    # 验证响应状态码
    assert response.status_code == 201

    # 验证响应数据
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == payload["email"]
    assert data["data"]["fullName"] == payload["full_name"]
    assert "id" in data["data"]
    assert "hashedPassword" not in data["data"]  # 确保不返回密码

@pytest.mark.anyio
async def test_register_existing_email(client: AsyncClient):
    # 准备注册数据
    payload = {
        "email": "duplicate@example.com",
        "password": "password123",
        "full_name": "First User",
        "phone": "13800000001",
        "campus": "Test Campus"
    }

    # 第一次注册
    response1 = await client.post("/api/auth/register", json=payload)
    assert response1.status_code == 201

    # 第二次使用相同邮箱注册
    response2 = await client.post("/api/auth/register", json=payload)

    # 验证应该失败
    assert response2.status_code == 400
    data = response2.json()
    assert data["success"] is False
    assert "该邮箱已注册" in data["message"]

@pytest.mark.anyio
async def test_register_invalid_data(client: AsyncClient):
    # 缺少必填字段 (password)
    payload = {
        "email": "invalid@example.com",
        "full_name": "Invalid User"
    }

    response = await client.post("/api/auth/register", json=payload)
    
    # 验证错误
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
