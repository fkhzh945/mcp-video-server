from fastapi import FastAPI, Query, Request
from typing import List, Dict, Optional, Any
import uvicorn
from datetime import datetime

# 调试日志函数
def debug_log(message: str):
    """打印带有时间戳的调试日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [DEBUG] {message}")

# 创建FastAPI应用实例
app = FastAPI(title="模拟视频服务API", description="用于模拟视频平台后端服务的API")

# 添加请求中间件用于日志记录
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有HTTP请求"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    debug_log(f"请求开始: {request.method} {request.url.path}")
    
    # 记录请求参数
    if request.query_params:
        debug_log(f"请求参数: {dict(request.query_params)}")
    
    response = await call_next(request)
    
    debug_log(f"请求结束: {request.method} {request.url.path} 状态码: {response.status_code}")
    return response

# 模拟设备数据
mock_devices = [
    {
        "device_id": "ca001",
        "name": "仓库门口摄像头",
        "type": "ip_camera",
        "status": "online",
        "ip_address": "192.168.1.101",
        "port": 554,
        "rtsp_url": "rtsp://192.168.1.101:554/stream1",
        "http_url": "http://192.168.1.101:80",
        "location": "仓库门口",
        "model": "Hikvision DS-2CD2042WD-I",
        "resolution": "1080p",
        "last_online": "2024-01-15 10:30:00",
        "manufacturer": "Hikvision",
        "firmware_version": "V5.4.5"
    },
    {
        "device_id": "ca002",
        "name": "仓库内部摄像头",
        "type": "ip_camera",
        "status": "online",
        "ip_address": "192.168.1.102",
        "port": 554,
        "rtsp_url": "rtsp://192.168.1.102:554/stream1",
        "http_url": "http://192.168.1.102:80",
        "location": "仓库内部",
        "model": "Dahua IPC-HDW1431TMP-AS",
        "resolution": "4K",
        "last_online": "2024-01-15 10:30:00",
        "manufacturer": "Dahua",
        "firmware_version": "V2.800.0000000.28.R.20190805"
    },
    {
        "device_id": "ca003",
        "name": "门口摄像头",
        "type": "ip_camera",
        "status": "offline",
        "ip_address": "192.168.1.103",
        "port": 554,
        "rtsp_url": "rtsp://192.168.1.103:554/stream1",
        "http_url": "http://192.168.1.103:80",
        "location": "公司门口",
        "model": "Axis P3225-LVE Mk III",
        "resolution": "1080p",
        "last_online": "2024-01-15 09:15:00",
        "manufacturer": "Axis",
        "firmware_version": "9.80.1"
    },
    {
        "device_id": "nv001",
        "name": "仓库NVR",
        "type": "nvr",
        "status": "online",
        "ip_address": "192.168.1.201",
        "port": 554,
        "rtsp_url": "rtsp://192.168.1.201:554/stream1",
        "http_url": "http://192.168.1.201:80",
        "location": "仓库机房",
        "model": "Hikvision DS-7732NI-K4",
        "resolution": "4K",
        "last_online": "2024-01-15 10:30:00",
        "manufacturer": "Hikvision",
        "firmware_version": "V4.30.000",
        "channels": 32
    },
    {
        "device_id": "nv002",
        "name": "办公楼NVR",
        "type": "nvr",
        "status": "online",
        "ip_address": "192.168.1.202",
        "port": 554,
        "rtsp_url": "rtsp://192.168.1.202:554/stream1",
        "http_url": "http://192.168.1.202:80",
        "location": "办公楼机房",
        "model": "Dahua NVR4232-4KS2",
        "resolution": "4K",
        "last_online": "2024-01-15 10:30:00",
        "manufacturer": "Dahua",
        "firmware_version": "V3.216.0000000.42.R.20200731",
        "channels": 32
    },
    {
        "device_id": "ca004",
        "name": "走廊摄像头1",
        "type": "ip_camera",
        "status": "online",
        "ip_address": "192.168.1.104",
        "port": 554,
        "rtsp_url": "rtsp://192.168.1.104:554/stream1",
        "http_url": "http://192.168.1.104:80",
        "location": "1楼走廊",
        "model": "Hikvision DS-2CD2045FWD-I",
        "resolution": "1080p",
        "last_online": "2024-01-15 10:29:00",
        "manufacturer": "Hikvision",
        "firmware_version": "V5.4.5"
    },
    {
        "device_id": "ca005",
        "name": "走廊摄像头2",
        "type": "ip_camera",
        "status": "online",
        "ip_address": "192.168.1.105",
        "port": 554,
        "rtsp_url": "rtsp://192.168.1.105:554/stream1",
        "http_url": "http://192.168.1.105:80",
        "location": "2楼走廊",
        "model": "Hikvision DS-2CD2045FWD-I",
        "resolution": "1080p",
        "last_online": "2024-01-15 10:29:00",
        "manufacturer": "Hikvision",
        "firmware_version": "V5.4.5"
    },
    {
        "device_id": "ca006",
        "name": "走廊摄像头3",
        "type": "ip_camera",
        "status": "online",
        "ip_address": "192.168.1.106",
        "port": 554,
        "rtsp_url": "rtsp://192.168.1.106:554/stream1",
        "http_url": "http://192.168.1.106:80",
        "location": "3楼走廊",
        "model": "Dahua IPC-HDW1431TMP-AS",
        "resolution": "1080p",
        "last_online": "2024-01-15 10:30:00",
        "manufacturer": "Dahua",
        "firmware_version": "V2.800.0000000.28.R.20190805"
    },
    {
        "device_id": "ca007",
        "name": "大会议室摄像头",
        "type": "ip_camera",
        "status": "online",
        "ip_address": "192.168.1.107",
        "port": 554,
        "rtsp_url": "rtsp://192.168.1.107:554/stream1",
        "http_url": "http://192.168.1.107:80",
        "location": "大会议室",
        "model": "Axis P3224-LV Mk III",
        "resolution": "4K",
        "last_online": "2024-01-15 10:30:00",
        "manufacturer": "Axis",
        "firmware_version": "9.80.1"
    },
    {
        "device_id": "ca008",
        "name": "小会议室摄像头",
        "type": "ip_camera",
        "status": "online",
        "ip_address": "192.168.1.108",
        "port": 554,
        "rtsp_url": "rtsp://192.168.1.108:554/stream1",
        "http_url": "http://192.168.1.108:80",
        "location": "小会议室A",
        "model": "Sony SNC-VB770D",
        "resolution": "1080p",
        "last_online": "2024-01-15 10:30:00",
        "manufacturer": "Sony",
        "firmware_version": "V6.20"
    }
]

def filter_devices(devices: List[Dict[str, Any]], device_type: Optional[str] = None, 
                  status: Optional[str] = None, keyword: Optional[str] = None) -> List[Dict[str, Any]]:
    """根据过滤条件筛选设备"""
    debug_log(f"开始过滤设备: device_type={device_type}, status={status}, keyword={keyword}")
    filtered_devices = devices
    
    # 按设备类型过滤
    if device_type:
        filtered_devices = [d for d in filtered_devices if d.get("type") == device_type]
    
    # 按状态过滤
    if status:
        filtered_devices = [d for d in filtered_devices if d.get("status") == status]
    
    # 按关键词模糊搜索
    if keyword:
        keyword = keyword.lower().strip()
        filtered_devices = [
            d for d in filtered_devices
            if keyword in str(d.get("name", "")).lower() or 
               keyword in str(d.get("device_id", "")).lower() or 
               keyword in str(d.get("location", "")).lower()
        ]
    
    debug_log(f"过滤完成，返回设备数量: {len(filtered_devices)}")
    return filtered_devices

@app.get("/api/devices", response_model=Dict[str, Any])
async def get_devices(
    type: Optional[str] = Query(None, description="设备类型过滤"),
    status: Optional[str] = Query(None, description="设备状态过滤"),
    keyword: Optional[str] = Query(None, description="关键词搜索")
):
    """查询设备列表，支持类型、状态过滤和关键词搜索"""
    debug_log(f"API调用: get_devices 参数: type={type}, status={status}, keyword={keyword}")
    # 应用过滤条件
    filtered_devices = filter_devices(mock_devices, device_type=type, status=status, keyword=keyword)
    
    # 返回结果，确保包含所有必要字段，特别是device_id和ip_address
    enhanced_devices = []
    for device in filtered_devices:
        # 确保每个设备对象都包含device_id和ip_address字段
        enhanced_device = {
            "device_id": device.get("device_id", ""),
            "ip_address": device.get("ip_address", ""),
            "name": device.get("name", ""),
            "type": device.get("type", ""),
            "status": device.get("status", ""),
            "location": device.get("location", ""),
            "model": device.get("model", ""),
            "resolution": device.get("resolution", ""),
            "last_online": device.get("last_online", ""),
            "manufacturer": device.get("manufacturer", ""),
            # 包含其他所有原始字段
            **device
        }
        enhanced_devices.append(enhanced_device)
    
    result = {
        "success": True,
        "data": enhanced_devices,
        "total": len(enhanced_devices)
    }
    debug_log(f"API响应: get_devices 返回设备总数: {len(enhanced_devices)}")
    return result

@app.get("/api/devices/{device_id}", response_model=Dict[str, Any])
async def get_device_info(device_id: str):
    """获取单个设备的详细信息"""
    debug_log(f"API调用: get_device_info 参数: device_id={device_id}")
    # 查找设备
    device = next((d for d in mock_devices if d.get("device_id") == device_id), None)
    
    if device:
        debug_log(f"API响应: get_device_info 找到设备: {device.get('name')}")
        return {
            "success": True,
            "data": device
        }
    else:
        debug_log(f"API响应: get_device_info 未找到设备: {device_id}")
        return {
            "success": False,
            "error": "设备不存在"
        }

@app.post("/api/devices/{device_id}/live-view", response_model=Dict[str, Any])
async def start_live_view(device_id: str):
    """启动设备实时预览"""
    debug_log(f"API调用: start_live_view 参数: device_id={device_id}")
    # 查找设备
    device = next((d for d in mock_devices if d.get("device_id") == device_id), None)
    
    if device:
        debug_log(f"API响应: start_live_view 找到设备: {device.get('name')}，返回RTSP地址")
        return {
            "success": True,
            "rtsp_url": device.get("rtsp_url"),
            "proxy_url": f"http://localhost:8001/rtsp/{device_id}"
        }
    else:
        debug_log(f"API响应: start_live_view 未找到设备: {device_id}")
        return {
            "success": False,
            "error": "设备不存在"
        }

@app.post("/api/devices/{device_id}/playback", response_model=Dict[str, Any])
async def playback_record(device_id: str, start_time: str, end_time: str):
    """回放录像"""
    debug_log(f"API调用: playback_record 参数: device_id={device_id}, start_time={start_time}, end_time={end_time}")
    # 查找设备
    device = next((d for d in mock_devices if d.get("device_id") == device_id), None)
    
    if device:
        debug_log(f"API响应: playback_record 找到设备: {device.get('name')}，生成回放URL")
        return {
            "success": True,
            "playback_url": f"http://localhost:8001/playback/{device_id}/{start_time}/{end_time}"
        }
    else:
        debug_log(f"API响应: playback_record 未找到设备: {device_id}")
        return {
            "success": False,
            "error": "设备不存在"
        }

@app.get("/api/stream-url", response_model=Dict[str, Any])
async def get_stream_url(
    device_id: Optional[str] = Query(None, description="设备ID"),
    name: Optional[str] = Query(None, description="设备名称")
):
    """通过设备ID或名称查询设备的拉流地址信息"""
    debug_log(f"API调用: get_stream_url 参数: device_id={device_id}, name={name}")
    # 至少需要提供device_id或name中的一个
    if not device_id and not name:
        debug_log(f"API响应: get_stream_url 错误: 缺少必要参数")
        return {
            "success": False,
            "error": "必须提供device_id或name参数"
        }
    
    # 查找设备
    device = None
    if device_id:
        device = next((d for d in mock_devices if d.get("device_id") == device_id), None)
    elif name:
        # 按名称模糊匹配
        matching_devices = [d for d in mock_devices if name.lower() in d.get("name", "").lower()]
        if matching_devices:
            device = matching_devices[0]  # 返回第一个匹配的设备
    
    if device:
        debug_log(f"API响应: get_stream_url 找到设备: {device.get('name')}，返回流地址信息")
        return {
            "success": True,
            "data": {
                "device_id": device.get("device_id"),
                "device_name": device.get("name"),
                "rtsp_url": device.get("rtsp_url"),
                "http_url": device.get("http_url"),
                "ip_address": device.get("ip_address"),
                "port": device.get("port"),
                "status": device.get("status"),
                # 提供额外的流地址格式
                "hls_url": f"http://localhost:8001/hls/{device.get('device_id')}/stream.m3u8",
                "webrtc_url": f"http://localhost:8001/webrtc/{device.get('device_id')}"
            }
        }
    else:
        debug_log(f"API响应: get_stream_url 未找到匹配设备: device_id={device_id}, name={name}")
        return {
            "success": False,
            "error": "未找到匹配的设备"
        }

if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    debug_log("启动模拟视频服务API服务器...")
    debug_log("API地址: http://localhost:8001")
    debug_log("文档地址: http://localhost:8001/docs")
    debug_log("可用接口:")
    debug_log("  GET  /api/devices - 查询设备列表(支持过滤和搜索)")
    debug_log("  GET  /api/devices/{device_id} - 获取设备详细信息")
    debug_log("  POST /api/devices/{device_id}/live-view - 启动实时预览")
    debug_log("  POST /api/devices/{device_id}/playback - 回放录像")
    debug_log("  GET  /api/stream-url - 通过设备ID或名称查询拉流地址")
    
    try:
        debug_log("开始启动uvicorn服务器...")
        uvicorn.run(app, host="0.0.0.0", port=8001)
    except KeyboardInterrupt:
        debug_log("接收到键盘中断，正在关闭服务器...")
    except Exception as e:
        debug_log(f"服务器异常: {str(e)}")
    finally:
        debug_log("服务器已停止")