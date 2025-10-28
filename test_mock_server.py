# -*- coding: utf-8 -*-
import json
import requests
import sys
import time
import subprocess

"""
简单测试脚本，用于测试mock_video_server.py的API端点
"""

# 模拟视频服务器的默认端口
MOCK_SERVER_PORT = 5005
MOCK_SERVER_URL = f"http://127.0.0.1:{MOCK_SERVER_PORT}"

def check_mock_server_status():
    """检查模拟视频服务器状态"""
    print(f"检查模拟视频服务器状态: {MOCK_SERVER_URL}")
    
    try:
        # 尝试连接服务器
        response = requests.get(MOCK_SERVER_URL, timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        return True
    except Exception as e:
        print(f"❌ 无法连接到模拟视频服务器: {str(e)}")
        return False

def test_simple_endpoints():
    """测试简单的API端点"""
    endpoints = [
        "/",
        "/status",
        "/health",
        "/api",
        "/video"
    ]
    
    print("\n测试简单端点:")
    for endpoint in endpoints:
        url = f"{MOCK_SERVER_URL}{endpoint}"
        print(f"\n测试端点: {url}")
        try:
            response = requests.get(url, timeout=5)
            print(f"状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")

def test_mcp_endpoint():
    """测试MCP端点"""
    mcp_url = f"{MOCK_SERVER_URL}/mcp"
    print(f"\n测试MCP端点: {mcp_url}")
    
    # 尝试简单的JSON-RPC请求
    payload = {
        "jsonrpc": "2.0",
        "method": "get_video_devices",
        "params": {},
        "id": "1"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            mcp_url,
            headers=headers,
            json=payload,
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")

def main():
    print("=== 模拟视频服务器测试 ===")
    
    # 先检查服务器状态
    if not check_mock_server_status():
        print("\n❌ 服务器似乎未运行。尝试启动服务器:")
        print("运行 'python mock_video_server.py' 启动模拟视频服务器")
        return
    
    # 测试简单端点
    test_simple_endpoints()
    
    # 测试MCP端点
    test_mcp_endpoint()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()