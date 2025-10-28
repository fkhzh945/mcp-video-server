import requests
import json

def test_mock_video_server():
    """直接测试mock_video_server是否正常工作"""
    print("开始测试模拟视频服务器API...")
    
    # 测试获取设备列表
    print("\n测试1: 获取设备列表")
    try:
        response = requests.get("http://localhost:8001/api/devices")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应: 成功={data.get('success')}")
            print(f"设备数量: {data.get('total', 0)}")
            if data.get('data') and len(data['data']) > 0:
                print(f"第一个设备: {data['data'][0]['name']}")
        else:
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"测试失败: {str(e)}")
    
    # 测试获取设备详情（如果有设备的话）
    print("\n测试2: 获取设备详情")
    try:
        # 使用一个已知的设备ID（从mock_video_server.py中看到的）
        device_id = "device_1"
        response = requests.get(f"http://localhost:8001/api/devices/{device_id}")
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应: 成功={data.get('success')}")
            if data.get('data'):
                print(f"设备名称: {data['data'].get('name')}")
                print(f"设备状态: {data['data'].get('status')}")
        else:
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"测试失败: {str(e)}")
    
    print("\n视频服务器API测试完成")

if __name__ == "__main__":
    test_mock_video_server()