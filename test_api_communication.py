"""
测试API通信机制的脚本
验证优化后的前后端通信是否正常工作
"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api"

def test_health_check():
    """测试健康检查端点"""
    try:
        response = requests.get(f"{BASE_URL}/../healthz")
        print(f"健康检查: {response.status_code}, {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

def test_api_endpoints():
    """测试主要API端点"""
    endpoints = [
        "/users/me",
        "/tasks",
        "/auth/login",
        "/auth/register",
        "/maps/geocode",
        "/maps/reverse-geocode"
    ]
    
    print("\n测试API端点可达性:")
    for endpoint in endpoints:
        try:
            # 对于需要认证的端点，我们只检查是否返回了适当的错误码
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"  {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"  {endpoint}: 错误 - {e}")

def test_request_id():
    """测试请求ID功能"""
    try:
        response = requests.get(f"{BASE_URL}/../healthz")
        request_id = response.headers.get('X-Request-ID')
        print(f"\n请求ID测试: {request_id}")
        return request_id is not None
    except Exception as e:
        print(f"请求ID测试失败: {e}")
        return False

def test_error_handling():
    """测试错误处理"""
    try:
        # 测试一个不存在的端点
        response = requests.get(f"{BASE_URL}/nonexistent/endpoint")
        print(f"\n错误处理测试 - 状态码: {response.status_code}")
        print(f"错误处理测试 - 响应: {response.json()}")
        return response.status_code == 404
    except Exception as e:
        print(f"错误处理测试失败: {e}")
        return False

def main():
    print("开始测试API通信机制...")
    
    success = True
    
    # 测试健康检查
    if not test_health_check():
        success = False
    
    # 测试API端点
    test_api_endpoints()
    
    # 测试请求ID
    if not test_request_id():
        print("警告: 请求ID功能未正常工作")
    
    # 测试错误处理
    if not test_error_handling():
        print("警告: 错误处理可能存在问题")
    
    print(f"\nAPI通信测试完成，总体状态: {'通过' if success else '部分失败'}")
    
    # 额外测试 - 地理编码API
    print("\n测试地理编码API（需要配置API密钥）:")
    try:
        response = requests.get(f"{BASE_URL}/maps/geocode?address=北京市")
        print(f"  地理编码API响应: {response.status_code}")
    except Exception as e:
        print(f"  地理编码API测试失败: {e}")
    
    # 测试逆地理编码API
    try:
        response = requests.get(f"{BASE_URL}/maps/reverse-geocode?lng=116.397428&lat=39.90923")
        print(f"  逆地理编码API响应: {response.status_code}")
    except Exception as e:
        print(f"  逆地理编码API测试失败: {e}")

if __name__ == "__main__":
    main()