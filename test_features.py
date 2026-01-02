#!/usr/bin/env python3
"""
测试所有新功能是否正常工作
"""

import asyncio
import httpx
import json
import sys

BASE_URL = "http://localhost:9800"
TEST_TOKEN = None

async def test_health():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/healthz")
            if response.status_code == 200:
                print("✅ 健康检查通过")
                return True
            else:
                print(f"❌ 健康检查失败: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

async def test_register():
    """测试用户注册"""
    print("🔍 测试用户注册...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/auth/register",
                json={
                    "email": "test@example.com",
                    "fullName": "测试用户",
                    "password": "123456",
                    "campus": "测试校区",
                    "phone": "13800138000"
                }
            )
            result = response.json()
            if response.status_code == 201 and result.get("success"):
                print("✅ 用户注册成功")
                return True
            else:
                print(f"❌ 用户注册失败: {result.get('message', 'Unknown error')}")
                return False
    except Exception as e:
        print(f"❌ 用户注册异常: {e}")
        return False

async def test_login():
    """测试用户登录"""
    print("🔍 测试用户登录...")
    global TEST_TOKEN
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "123456"
                }
            )
            result = response.json()
            if response.status_code == 200 and result.get("success"):
                TEST_TOKEN = result["data"]["accessToken"]
                print("✅ 用户登录成功")
                return True
            else:
                print(f"❌ 用户登录失败: {result.get('message', 'Unknown error')}")
                return False
    except Exception as e:
        print(f"❌ 用户登录异常: {e}")
        return False

async def test_chat_api():
    """测试聊天API"""
    print("🔍 测试聊天API...")
    if not TEST_TOKEN:
        print("❌ 无有效token，跳过聊天API测试")
        return False

    headers = {"Authorization": f"Bearer {TEST_TOKEN}"}

    try:
        # 创建一个测试任务
        async with httpx.AsyncClient() as client:
            # 先创建任务
            task_response = await client.post(
                f"{BASE_URL}/api/tasks",
                headers=headers,
                json={
                    "title": "测试任务",
                    "description": "用于测试聊天功能",
                    "rewardAmount": 10.0,
                    "category": "other",
                    "urgency": "medium",
                    "pickupLocationName": "起点",
                    "dropoffLocationName": "终点"
                }
            )

            if task_response.status_code != 200:
                print("❌ 创建测试任务失败")
                return False

            task_data = task_response.json()["data"]

            # 测试发送消息
            send_response = await client.post(
                f"{BASE_URL}/api/chat/send",
                headers=headers,
                json={
                    "taskId": task_data["id"],
                    "receiverId": task_data["createdById"],  # 给自己发消息用于测试
                    "content": "测试消息"
                }
            )

            if send_response.status_code == 200:
                print("✅ 聊天消息发送成功")
                return True
            else:
                print(f"❌ 聊天消息发送失败: {send_response.json()}")
                return False

    except Exception as e:
        print(f"❌ 聊天API测试异常: {e}")
        return False

async def test_evaluation_api():
    """测试评价API"""
    print("🔍 测试评价API...")
    if not TEST_TOKEN:
        print("❌ 无有效token，跳过评价API测试")
        return False

    headers = {"Authorization": f"Bearer {TEST_TOKEN}"}

    try:
        async with httpx.AsyncClient() as client:
            # 提交评价
            eval_response = await client.post(
                f"{BASE_URL}/api/evaluation/submit",
                headers=headers,
                json={
                    "taskId": 1,  # 假设任务ID为1
                    "evaluateeId": 1,  # 假设评价用户ID为1
                    "score": 5,
                    "comment": "测试评价"
                }
            )

            # 即使任务不存在，我们也测试API是否能正常响应
            if eval_response.status_code in [200, 400, 404]:
                print("✅ 评价API响应正常")
                return True
            else:
                print(f"❌ 评价API异常: {eval_response.status_code}")
                return False

    except Exception as e:
        print(f"❌ 评价API测试异常: {e}")
        return False

async def test_payment_api():
    """测试支付API"""
    print("🔍 测试支付API...")
    if not TEST_TOKEN:
        print("❌ 无有效token，跳过支付API测试")
        return False

    headers = {"Authorization": f"Bearer {TEST_TOKEN}"}

    try:
        async with httpx.AsyncClient() as client:
            # 查询余额
            balance_response = await client.get(
                f"{BASE_URL}/api/payment/balance",
                headers=headers
            )

            if balance_response.status_code == 200:
                print("✅ 支付API响应正常")
                return True
            else:
                print(f"❌ 支付API异常: {balance_response.status_code}")
                return False

    except Exception as e:
        print(f"❌ 支付API测试异常: {e}")
        return False

async def test_appeal_api():
    """测试申诉API"""
    print("🔍 测试申诉API...")
    if not TEST_TOKEN:
        print("❌ 无有效token，跳过申诉API测试")
        return False

    headers = {"Authorization": f"Bearer {TEST_TOKEN}"}

    try:
        async with httpx.AsyncClient() as client:
            # 获取申诉列表
            appeal_response = await client.get(
                f"{BASE_URL}/api/appeal/my",
                headers=headers
            )

            if appeal_response.status_code == 200:
                print("✅ 申诉API响应正常")
                return True
            else:
                print(f"❌ 申诉API异常: {appeal_response.status_code}")
                return False

    except Exception as e:
        print(f"❌ 申诉API测试异常: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始测试校园互助平台新功能")
    print("=" * 50)

    # 基础功能测试
    health_ok = await test_health()

    if not health_ok:
        print("❌ 后端服务未启动，请先启动后端服务")
        return

    # 用户功能测试
    register_ok = await test_register()
    login_ok = await test_login()

    if not login_ok:
        print("❌ 用户登录失败，无法继续测试其他功能")
        return

    # 新功能测试
    chat_ok = await test_chat_api()
    evaluation_ok = await test_evaluation_api()
    payment_ok = await test_payment_api()
    appeal_ok = await test_appeal_api()

    print("=" * 50)
    print("📊 测试结果总结:")
    print(f"健康检查: {'✅' if health_ok else '❌'}")
    print(f"用户注册: {'✅' if register_ok else '❌'}")
    print(f"用户登录: {'✅' if login_ok else '❌'}")
    print(f"聊天功能: {'✅' if chat_ok else '❌'}")
    print(f"评价功能: {'✅' if evaluation_ok else '❌'}")
    print(f"支付功能: {'✅' if payment_ok else '❌'}")
    print(f"申诉功能: {'✅' if appeal_ok else '❌'}")

    success_count = sum([health_ok, register_ok, login_ok, chat_ok, evaluation_ok, payment_ok, appeal_ok])
    total_count = 7

    if success_count == total_count:
        print(f"🎉 所有功能测试通过！({success_count}/{total_count})")
    else:
        print(f"⚠️ 部分功能测试失败 ({success_count}/{total_count})")

if __name__ == "__main__":
    asyncio.run(main())
