import sys
import subprocess
import json
import os
import asyncio

async def test_video_server_tools():
    print("开始测试视频服务器工具...")
    
    # 检查服务是否运行
    print("\n测试服务是否运行")
    try:
        # 使用Python的server.py脚本检查状态
        result = subprocess.run(["python", "server.py", "status"], 
                               capture_output=True, text=True)
        print(f"状态检查输出: {result.stdout}")
        if "is running" not in result.stdout:
            print("❌ MCP服务器未运行，请先启动服务器")
            return
    except Exception as e:
        print(f"状态检查失败: {str(e)}")
        return
    
    # 直接导入并调用工具函数
    print("\n" + "="*50)
    print("直接测试MCP服务器工具函数")
    print("="*50)
    
    try:
        # 添加当前目录到Python路径
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # 导入server.py中的工具函数
        from server import get_video_devices, get_device_details, start_live_preview, playback_recording, get_stream_url
        
        # 测试get_video_devices (异步调用)
        print("\n1. 测试 get_video_devices")
        print("-"*30)
        result = await get_video_devices()
        print(f"✅ 成功调用 get_video_devices")
        devices = result.get('devices', [])
        print(f"返回设备数量: {len(devices)}")
        if devices:
            print(f"第一个设备ID: {devices[0].get('device_id')}")
            
            # 使用第一个设备ID测试其他工具
            device_id = devices[0].get('device_id')
            
            # 测试get_device_details (异步调用)
            print("\n2. 测试 get_device_details")
            print("-"*30)
            details = await get_device_details(device_id=device_id)
            print(f"✅ 成功调用 get_device_details")
            print(f"设备名称: {details.get('name')}")
            print(f"设备类型: {details.get('type')}")
            
            # 测试start_live_preview (异步调用)
            print("\n3. 测试 start_live_preview")
            print("-"*30)
            preview = await start_live_preview(device_id=device_id)
            print(f"✅ 成功调用 start_live_preview")
            print(f"预览URL: {preview.get('preview_url')}")
            
            # 测试playback_recording (异步调用)
            print("\n4. 测试 playback_recording")
            print("-"*30)
            playback = await playback_recording(device_id=device_id, start_time="2023-01-01T00:00:00", end_time="2023-01-01T01:00:00")
            print(f"✅ 成功调用 playback_recording")
            print(f"回放URL: {playback.get('playback_url')}")
            
            # 测试get_stream_url (RTSP) (异步调用)
            print("\n5. 测试 get_stream_url (RTSP)")
            print("-"*30)
            rtsp_url = await get_stream_url(device_id=device_id, stream_type="RTSP")
            print(f"✅ 成功调用 get_stream_url (RTSP)")
            print(f"RTSP URL: {rtsp_url.get('stream_url')}")
            
            # 测试get_stream_url (HTTP) (异步调用)
            print("\n6. 测试 get_stream_url (HTTP)")
            print("-"*30)
            http_url = await get_stream_url(device_id=device_id, stream_type="HTTP")
            print(f"✅ 成功调用 get_stream_url (HTTP)")
            print(f"HTTP URL: {http_url.get('stream_url')}")
            
            print("\n" + "="*50)
            print("🎉 所有工具测试成功完成!")
            print("="*50)
        else:
            print("⚠️  未找到任何视频设备，无法测试其他工具")
            
    except ImportError as e:
        print(f"❌ 导入工具函数失败: {str(e)}")
    except Exception as e:
        print(f"❌ 工具调用失败: {str(e)}")

if __name__ == "__main__":
    # 运行异步函数
    asyncio.run(test_video_server_tools())