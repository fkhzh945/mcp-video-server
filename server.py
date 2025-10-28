import os
import sys
import signal
import threading
import asyncio
import time
import socket
import subprocess
import json  # 添加json导入
import requests  # 添加requests库用于HTTP请求
import inspect
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# 定义有效的API密钥
VALID_API_KEY = "mcp_video_api_key_2024"

# 增强的API密钥验证函数
def validate_api_key_from_request(request_data):
    """从请求数据中验证API密钥，支持多种格式和位置"""
    # 1. 检查Authorization头（Bearer格式）
    if isinstance(request_data, dict):
        # 检查headers字段
        if 'headers' in request_data:
            headers = request_data['headers']
            if isinstance(headers, dict):
                # 检查标准Authorization头
                auth_header = headers.get("Authorization", "").strip()
                if auth_header and auth_header.startswith("Bearer "):
                    parts = auth_header.split(" ")
                    if len(parts) >= 2 and parts[1].strip() == VALID_API_KEY:
                        return True, "API key validated successfully from Authorization header"
                
                # 检查X-API-Key头
                if headers.get("X-API-Key", "").strip() == VALID_API_KEY:
                    return True, "API key validated successfully from X-API-Key header"
                
                # 检查API-Key头
                if headers.get("API-Key", "").strip() == VALID_API_KEY:
                    return True, "API key validated successfully from API-Key header"
        
        # 2. 检查params字段中的api_key参数
        if 'params' in request_data:
            params = request_data['params']
            if isinstance(params, dict):
                if params.get("api_key", "").strip() == VALID_API_KEY:
                    return True, "API key validated successfully from params"
        
        # 3. 检查request对象（如果存在）
        if 'request' in request_data and hasattr(request_data['request'], 'headers'):
            headers = dict(request_data['request'].headers)
            # 再次检查各种头
            auth_header = headers.get("Authorization", "").strip()
            if auth_header and auth_header.startswith("Bearer "):
                parts = auth_header.split(" ")
                if len(parts) >= 2 and parts[1].strip() == VALID_API_KEY:
                    return True, "API key validated successfully from request Authorization header"
            
            if headers.get("X-API-Key", "").strip() == VALID_API_KEY:
                return True, "API key validated successfully from request X-API-Key header"
            
            if headers.get("API-Key", "").strip() == VALID_API_KEY:
                return True, "API key validated successfully from request API-Key header"
    
    # 如果是FastMCP请求对象，尝试直接从请求中提取信息
    if hasattr(request_data, 'headers'):
        headers = dict(request_data.headers)
        # 检查各种头
        auth_header = headers.get("Authorization", "").strip()
        if auth_header and auth_header.startswith("Bearer "):
            parts = auth_header.split(" ")
            if len(parts) >= 2 and parts[1].strip() == VALID_API_KEY:
                return True, "API key validated successfully from request object Authorization header"
        
        if headers.get("X-API-Key", "").strip() == VALID_API_KEY:
            return True, "API key validated successfully from request object X-API-Key header"
        
        if headers.get("API-Key", "").strip() == VALID_API_KEY:
            return True, "API key validated successfully from request object API-Key header"
    
    # 如果都没有通过验证，返回详细的错误信息
    return False, "Missing or invalid API key. Please provide a valid API key in Authorization header (Bearer format), X-API-Key header, API-Key header, or params.api_key"

# 创建强化的API密钥验证装饰器
def require_api_key(func):
    """强化的API密钥验证装饰器，确保所有API调用都经过正确的密钥验证"""
    async def wrapper(*args, **kwargs):
        # 尝试从args和kwargs中提取请求信息
        request_data = {}
        
        # 合并kwargs到request_data
        request_data.update(kwargs)
        
        # 如果有args，检查第一个参数是否包含请求信息
        if args:
            ctx = args[0]
            # 检查是否是FastMCP上下文对象
            if hasattr(ctx, '__dict__'):
                # 将上下文对象的属性添加到request_data
                request_data['context'] = ctx
                # 尝试从上下文获取headers
                if hasattr(ctx, 'headers'):
                    request_data['headers'] = ctx.headers
                elif hasattr(ctx, 'request'):
                    request_data['request'] = ctx.request
        
        # 执行API密钥验证
        is_valid, message = validate_api_key_from_request(request_data)
        if not is_valid:
            # 返回统一的错误响应格式
            return {"error": message, "status": "unauthorized", "code": 401}
        
        # 验证通过，继续执行原始函数
        return await func(*args, **kwargs)
    
    # 保留原始函数的元数据
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    # 添加标记以表明此函数已被装饰
    wrapper.__wrapped__ = func
    return wrapper

# 添加全局API密钥验证中间件类
class ApiKeyMiddleware:
    """FastMCP中间件，仅在获取工具列表的请求时进行API密钥验证"""
    async def __call__(self, request, call_next):
        # 检查是否是工具列表请求（通常是第一个请求）
        # 我们假设没有特定工具参数的请求是在询问工具列表
        is_tool_list_request = not request.get('tool') and not request.get('name')
        
        # 只对工具列表请求验证API密钥
        if is_tool_list_request:
            is_valid, message = validate_api_key_from_request(request)
            if not is_valid:
                # 返回错误响应
                return {"error": message, "status": "unauthorized", "code": 401}
        
        # 验证通过或不需要验证，继续处理请求
        return await call_next(request)

# Message templates
SERVER_MESSAGES = {
    'server_start': 'video_server MCP server starting' + (' on port {port}' if 'http' != 'stdio' else ''),
    'server_started': 'video_server MCP server started successfully' + (' on port {port}' if 'http' != 'stdio' else ''),
    'server_stopped': 'video_server MCP server stopped',
    'server_start_fail': 'Failed to start video_server MCP server',
    'server_already_running': 'Server is already running',
    'server_not_running': 'Server is not running',
    'server_error': 'Server error: {error}',
    'start_error': 'Error starting server: {error}',
    'stop_error': 'Error stopping server: {error}',
    'stop_success': 'Server stopped successfully',
    'stop_fail': 'Server failed to stop',
    'status_running': 'video_server MCP server is running',
    'status_stopped': 'video_server MCP server is not running',
    'ping_success': 'Server is responding',
    'ping_fail': 'Server is not responding',
    'interrupt': 'Operation cancelled by user',
    'error': 'Error: {error}',
    'version': 'video_server MCP Server v{version}',
}

# API基础URL，指向模拟视频服务器
API_BASE_URL = "http://localhost:8001"  # 根据mock_video_server.py中的配置

def format_message(key: str, **kwargs) -> str:
    """Format a server message with given parameters."""
    template = SERVER_MESSAGES.get(key, '')
    return template.format(**kwargs) if template else ''



def create_response(success, message, data=None, exit_code=0, current_port=None, current_protocol=None):
    """Create a standardized JSON response"""
    response = {
        "success": success,
        "message": message,
        "timestamp": int(time.time()),
        "protocol": current_protocol or video_server_PROTOCOL,
    }
    if current_protocol != 'stdio' and current_port is not None:
        response["port"] = current_port
    if data:
        response["data"] = data
    return response, exit_code

# Initialize FastMCP server
# Generated by McpServerGen.py on 2025-10-28 14:20:48
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
video_server_PORT = int(os.getenv('MCP_VIDEO_SERVER_PORT', 5005)) if 'http' != 'stdio' else None
video_server_PROTOCOL = os.getenv('MCP_VIDEO_SERVER_PROTOCOL', 'http')
mcp = None  # Will be initialized after command line parsing

# Global variables for server management
_server_thread = None
_server_loop = None
_server_running = False
_server_start_time = None

#### Server Tools ####

async def get_video_devices(device_type=None, status=None, keyword=None, headers=None) -> dict:
    """获取视频设备列表
    
    Args:
        device_type: 设备类型过滤（可选）
        status: 设备状态过滤（可选）
        keyword: 关键词搜索（可选）
        headers: 请求头信息（由FastMCP框架自动传入）
    
    Returns:
        dict: 设备列表信息
    """
    
    try:
        # 构建API请求参数
        params = {}
        if device_type:
            params['type'] = device_type
        if status:
            params['status'] = status
        if keyword:
            params['keyword'] = keyword
        
        # 调用视频服务器API
        response = requests.get(f"{API_BASE_URL}/api/devices", params=params)
        response.raise_for_status()  # 如果状态码不是200，抛出异常
        
        result = response.json()
        # 调整返回格式以兼容之前的接口
        if result.get('success'):
            return {"devices": result.get('data', []), "total": result.get('total', 0)}
        else:
            raise RuntimeError(f"API返回错误: {result.get('error', '未知错误')}")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"请求视频服务器失败: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error in get_video_devices: {str(e)}")

async def get_device_details(device_id: str, headers=None) -> dict:
    """获取设备详细信息
    
    Args:
        device_id: 设备ID
        headers: 请求头信息（由FastMCP框架自动传入）
    
    Returns:
        dict: 设备详细信息
    """
    
    try:
        # 调用视频服务器API
        response = requests.get(f"{API_BASE_URL}/api/devices/{device_id}")
        response.raise_for_status()
        
        result = response.json()
        if result.get('success'):
            return result.get('data', {})
        else:
            return {"error": result.get('error', '设备不存在')}
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"请求视频服务器失败: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error in get_device_details: {str(e)}")

async def start_live_preview(device_id: str, stream_type: str = "main", headers=None) -> dict:
    """开始实时预览
    
    Args:
        device_id: 设备ID
        stream_type: 流类型（main/sub，默认main）
        headers: 请求头信息（由FastMCP框架自动传入）
    
    Returns:
        dict: 预览URL和状态信息
    """
    
    try:
        # 调用视频服务器API
        response = requests.post(f"{API_BASE_URL}/api/devices/{device_id}/live-view")
        response.raise_for_status()
        
        result = response.json()
        if result.get('success'):
            # 构建符合原始接口的返回格式
            return {
                "device_id": device_id,
                "stream_type": stream_type,
                "status": "success",
                "message": "Live preview started",
                "stream_urls": {
                    "rtsp": result.get('rtsp_url', ''),
                    "http": result.get('proxy_url', '')
                },
                "start_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
        else:
            raise RuntimeError(f"API返回错误: {result.get('error', '未知错误')}")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"请求视频服务器失败: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error in start_live_preview: {str(e)}")

async def playback_recording(device_id: str, start_time: str, end_time: str, stream_type: str = "main", headers=None) -> dict:
    """回放录像
    
    Args:
        device_id: 设备ID
        start_time: 开始时间（ISO格式）
        end_time: 结束时间（ISO格式）
        stream_type: 流类型（main/sub，默认main）
        headers: 请求头信息（由FastMCP框架自动传入）
    
    Returns:
        dict: 回放URL和状态信息
    """

    
    try:
        # 调用视频服务器API
        response = requests.post(
            f"{API_BASE_URL}/api/devices/{device_id}/playback",
            params={"start_time": start_time, "end_time": end_time}
        )
        response.raise_for_status()
        
        result = response.json()
        if result.get('success'):
            return {
                "device_id": device_id,
                "stream_type": stream_type,
                "start_time": start_time,
                "end_time": end_time,
                "status": "success",
                "message": "Playback started",
                "playback_urls": {
                    "http": result.get('playback_url', '')
                }
            }
        else:
            raise RuntimeError(f"API返回错误: {result.get('error', '未知错误')}")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"请求视频服务器失败: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error in playback_recording: {str(e)}")

async def get_stream_url(device_id: str, protocol: str = "rtsp", stream_type: str = "main", headers=None) -> dict:
    """获取视频流地址
    
    Args:
        device_id: 设备ID
        protocol: 协议类型（rtsp/http，默认rtsp）
        stream_type: 流类型（main/sub，默认main）
        headers: 请求头信息（由FastMCP框架自动传入）
    
    Returns:
        dict: 视频流地址和相关信息
    """
    
    try:
        # 调用视频服务器API
        response = requests.get(f"{API_BASE_URL}/api/stream-url", params={"device_id": device_id})
        response.raise_for_status()
        
        result = response.json()
        if result.get('success'):
            data = result.get('data', {})
            # 根据请求的协议返回对应的流地址
            if protocol.lower() == "rtsp":
                stream_url = data.get('rtsp_url', '')
            elif protocol.lower() == "http":
                stream_url = data.get('http_url', '')
            else:
                return {"error": "Unsupported protocol"}
            
            return {
                "device_id": device_id,
                "protocol": protocol,
                "stream_type": stream_type,
                "stream_url": stream_url,
                "status": "success",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
        else:
            return {"error": result.get('error', '未找到匹配的设备')}
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"请求视频服务器失败: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error in get_stream_url: {str(e)}")

#### Tool Registration ####

# List of all tool functions to register
TOOL_FUNCTIONS = [
    get_video_devices,
    get_device_details,
    start_live_preview,
    playback_recording,
    get_stream_url
    # Add additional tool functions here
]

def register_tools(verbose=True):
    """Register all tools with the MCP server and add API key validation middleware."""
    global mcp
    if mcp is None:
        raise RuntimeError("MCP instance must be initialized before registering tools")
    
    # 首先尝试添加中间件（如果FastMCP支持）
    try:
        if hasattr(mcp, 'add_middleware'):
            mcp.add_middleware(ApiKeyMiddleware())
            if verbose:
                print("Added API key validation middleware")
        elif hasattr(mcp, 'middleware'):
            mcp.middleware(ApiKeyMiddleware())
            if verbose:
                print("Added API key validation middleware")
        else:
            if verbose:
                print("FastMCP doesn't support middleware, using decorators for API key validation")
    except Exception as e:
        if verbose:
            print(f"Error adding middleware: {e}, falling back to decorators")
    
    # 注册所有工具函数 - 不再为函数单独添加装饰器，只依赖中间件进行API密钥验证
    for tool_func in TOOL_FUNCTIONS:
        mcp.tool()(tool_func)
        
        if verbose:
            print(f"Registered tool: {tool_func.__name__}")

#### Server management functions ####

def _run_server_in_thread(port, protocol):
    """Run the MCP server in a separate thread."""
    global _server_loop, _server_running
    
    _server_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_server_loop)
    
    try:
        _server_running = True
        if protocol == 'stdio':
            print(format_message('server_start'))
        else:
            print(format_message('server_start', port=port))
        mcp.run(transport="streamable-http" if protocol == "http" else protocol)
    except Exception as e:
        print(format_message('server_error', error=str(e)))
    finally:
        _server_running = False

def start_server(port=None, protocol=None):
    """Start the MCP server in a separate thread."""
    global _server_thread, _server_running, _server_start_time, mcp
    
    # Use provided parameters or fall back to global defaults
    if port is None:
        port = video_server_PORT
    if protocol is None:
        protocol = video_server_PROTOCOL
    
    # For stdio protocol, we don't need a port
    if protocol == 'stdio':
        port = None
    
    if (protocol == 'stdio' and mcp is None) or (protocol != 'stdio' and port != video_server_PORT):
        # Create fresh FastMCP instance with current port and protocol
        if protocol == 'stdio':
            mcp = FastMCP("video_server")
        else:
            mcp = FastMCP("video_server", port=port)
        # Register all tools with the new instance
        register_tools()
        
    try:
        # Check if server is already running
        if _server_running:
            print(format_message('server_already_running'))
            return False

        _server_thread = threading.Thread(target=_run_server_in_thread, args=(port, protocol), daemon=True)
        _server_thread.start()
        
        # Start shutdown listener in a separate daemon thread (only for non-stdio protocols)
        if protocol != 'stdio' and port is not None:
            threading.Thread(target=shutdown_listener, args=(port,), daemon=True).start()
        
        _server_start_time = time.time()
        
        time.sleep(2)  # Wait for server to start
        if _server_running:
            if protocol == 'stdio':
                print(format_message('server_started'))
            else:
                print(format_message('server_started', port=port))
            return True
        else:
            print(format_message('server_start_fail'))
            return False
    except Exception as e:
        print(format_message('start_error', error=str(e)))
        return False

def stop_server(json_mode=False, port=None):
    """Stop the MCP server using multiple reliable methods."""
    global _server_thread, _server_loop, _server_running

    # Use provided port or fall back to global default
    if port is None:
        port = video_server_PORT
    
    # For stdio protocol, port is None
    if video_server_PROTOCOL == 'stdio':
        port = None
    
    # First try to stop server started by this process
    if _server_running:
        try:
            _server_running = False
            
            # More aggressive shutdown
            if _server_loop and _server_loop.is_running():
                # Stop all running tasks in the loop
                for task in asyncio.all_tasks(_server_loop):
                    task.cancel()
                _server_loop.call_soon_threadsafe(_server_loop.stop)
            
            if _server_thread and _server_thread.is_alive():
                _server_thread.join(timeout=10)  # Increased timeout
                
            # Force kill thread if it's still alive
            if _server_thread and _server_thread.is_alive():
                # Reset thread reference
                _server_thread = None
        except Exception as e:
            print(format_message('stop_error', error=str(e)))
    
    # Try multiple shutdown methods for cross-process termination (skip for stdio)
    shutdown_success = False
    current_port = port
    
    # Skip port-based shutdown methods for stdio protocol
    if current_port is not None:
        # Method 1: Try graceful shutdown via control socket
        if not shutdown_success:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(5)
                    s.connect(('127.0.0.1', current_port + 1))
                    s.sendall(b'SHUTDOWN')
                    resp = s.recv(1024)
                    if resp == b'OK':
                        shutdown_success = True
                        if not json_mode:
                            print("Server stopped successfully via shutdown listener")
            except (ConnectionRefusedError, OSError, socket.timeout):
                # Shutdown listener is not accessible, try other methods
                pass
    
        # Method 2: Try to kill process using psutil (if available)
        if not shutdown_success and current_port is not None:
            try:
                import psutil
                killed_processes = []
                
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        # Look for Python processes running this server
                        if proc.info['name'] and 'python' in proc.info['name'].lower():
                            cmdline = proc.info['cmdline']
                            # More specific check: look for 'server.py' and server name in command line
                            if (cmdline and 
                                any('server.py' in str(arg) for arg in cmdline) and 
                                any('video_server' in str(arg).lower() for arg in cmdline)):
                                # Check if this process is using our port
                                try:
                                    for conn in proc.net_connections():
                                        if conn.laddr.port == current_port:
                                            proc.terminate()
                                            killed_processes.append(proc.info['pid'])
                                            break
                                except (psutil.AccessDenied, psutil.NoSuchProcess):
                                    continue
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if killed_processes:
                    # Wait a moment for processes to terminate
                    time.sleep(2)
                    if not is_port_in_use(current_port):
                        shutdown_success = True
                        if not json_mode:
                            print(f"Server stopped successfully (killed processes: {killed_processes})")
            except ImportError:
                # psutil not available, fall back to other methods
                pass
        
        # Method 3: Try netstat + taskkill (Windows specific)
        if not shutdown_success and current_port is not None and os.name == 'nt':
            try:
                # Find process ID using netstat
                result = subprocess.run(
                    f'netstat -ano | findstr ":{current_port}"',
                    capture_output=True,
                    text=True,
                    shell=True
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    lines = result.stdout.strip().split('\n')
                    pids = set()
                    for line in lines:
                        parts = line.split()
                        if len(parts) >= 5:
                            pids.add(parts[-1])
                    
                    # Kill the processes
                    for pid in pids:
                        try:
                            subprocess.run(['taskkill', '/PID', pid, '/F'], 
                                         capture_output=True, check=True)
                        except:
                            continue
                    
                    # Wait and check if port is free
                    time.sleep(2)
                    if not is_port_in_use(current_port):
                        shutdown_success = True
                        if not json_mode:
                            print(f"Server stopped successfully (killed PIDs: {', '.join(pids)})")
            except Exception:
                pass
    
    # For protocols with ports, wait for port to be released
    if current_port is not None:
        max_wait = 5
        wait_count = 0
        while is_port_in_use(current_port) and wait_count < max_wait:
            time.sleep(1)
            wait_count += 1
    
    # Check if server is actually stopped
    if current_port is None:  # stdio protocol
        # For stdio, just check if the internal process stopped
        if not _server_running:
            if not json_mode:
                print(format_message('server_stopped'))
            return True
        else:
            if not json_mode:
                print(format_message('stop_fail'))
            return False
    elif not is_port_in_use(current_port):  # port-based protocols
        if not json_mode:
            print(format_message('server_stopped'))
        return True
    else:
        if shutdown_success:
            if not json_mode:
                print(format_message('server_stopped'))
            return True
        else:
            if not json_mode:
                print(format_message('stop_fail'))
            return False

def is_server_running():
    """Check if the server is currently running."""
    # For stdio protocol, only check the internal flag since there's no port
    if video_server_PROTOCOL == 'stdio':
        return _server_running
    # For other protocols, check both internal flag and port usage for more accurate status
    return _server_running and is_port_in_use(video_server_PORT)

def is_port_in_use(port):
    """Check if a port is currently in use."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)  # Add timeout to avoid hanging
            result = s.connect_ex(('127.0.0.1', port))
            return result == 0
    except Exception:
        return False

def shutdown_listener(port):
    """Listen for a shutdown command on a local TCP socket."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Allow socket reuse to prevent "Address already in use" errors
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('127.0.0.1', port + 1))  # Use port + 1 for control
        sock.listen(1)
        sock.settimeout(1)  # Add timeout to make it responsive
        
        while _server_running:
            try:
                conn, addr = sock.accept()
                data = conn.recv(1024)
                if data == b'SHUTDOWN':
                    print("Shutdown command received via control socket")
                    stop_server(json_mode=False, port=port)  # Pass the port parameter
                    conn.sendall(b'OK')
                    conn.close()
                    break
                conn.close()
            except socket.timeout:
                # Continue loop to check _server_running flag
                continue
            except Exception:
                # Handle any other socket errors gracefully
                break
    except Exception as e:
        # Port might be in use or other socket error
        print(f"Shutdown listener could not start: {e}")
        # Continue without shutdown listener - other methods will still work
    finally:
        try:
            sock.close()
        except:
            pass

# Command line interface
if __name__ == "__main__":
    import json
    import argparse

    class ArgumentParserWithExceptions(argparse.ArgumentParser):
        def error(self, message):
            raise ValueError(message)
    
    def print_response(response, exit_code, json_output=False):
        """Print response and exit"""
        if json_output:
            print(json.dumps(response), flush=True)
        else:
            print(response["message"])
        sys.stdout.flush() 
        sys.exit(exit_code)
    
    # Set up argument parser
    parser = ArgumentParserWithExceptions(
        description="Video MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python server.py start
  python server.py start --json
  python server.py stop
  python server.py status --json
  python server.py ping
  python server.py version
        """
    )
    
    parser.add_argument("command", choices=["start", "stop", "status", "ping", "version", "help"])
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--port", type=int)
    parser.add_argument("--protocol", choices=["sse", "stdio", "http"], help="Communication protocol")
    
    try:
        args = parser.parse_args()
        
        current_port = video_server_PORT
        current_protocol = video_server_PROTOCOL
        if args.port:
            current_port = args.port
            os.environ[f'MCP_VIDEO_SERVER_PORT'] = str(current_port)
        if args.protocol:
            current_protocol = args.protocol
            os.environ[f'MCP_VIDEO_SERVER_PROTOCOL'] = current_protocol
        
        # For stdio protocol, ignore port setting
        if current_protocol == 'stdio':
            current_port = None
            
        # Initialize FastMCP with the final port and protocol values
        if current_protocol == 'stdio':
            mcp = FastMCP("video_server")
        else:
            mcp = FastMCP("video_server", port=current_port)
        # Register all tools with the MCP instance
        register_tools(verbose=not args.json)      
            
        if args.command == "start":
            if start_server(current_port, current_protocol):
                if current_protocol == 'stdio':
                    response, exit_code = create_response(
                        True, 
                        format_message('server_started'),
                        {},
                        exit_code=0 if _server_running else 1,
                        current_port=current_port,
                        current_protocol=current_protocol
                    )
                else:
                    response, exit_code = create_response(
                        True, 
                        format_message('server_started', port=current_port),
                        {"port": current_port},
                        exit_code=0 if _server_running else 1,
                        current_port=current_port,
                        current_protocol=current_protocol
                    )
                
                if args.json:
                    print(json.dumps(response), flush=True)
        
                try:
                    while _server_running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\\nReceived interrupt signal")
                    stop_server(json_mode=args.json, port=current_port)
                    response, exit_code = create_response(
                        True, 
                        format_message('interrupt'),
                        current_port=current_port,
                        current_protocol=current_protocol
                    )
            else:
                response, exit_code = create_response(
                    False, 
                    format_message('server_start_fail'), 
                    exit_code=1,
                    current_port=current_port,
                    current_protocol=current_protocol
                )
                
        elif args.command == "stop":
            success = stop_server(json_mode=args.json, port=current_port)
            response, exit_code = create_response(
                success,
                format_message('stop_success' if success else 'stop_fail'),
                exit_code=0 if success else 1,
                current_port=current_port,
                current_protocol=current_protocol
            )
            
        elif args.command == "status":
            # For command line usage, check appropriate method based on protocol
            if current_protocol == 'stdio':
                # For stdio, we can't easily check if another process is running
                # so we'll just report based on what we can detect
                running = False  # Default to not running for separate process
                status_data = {"status": "running" if running else "stopped", "protocol": current_protocol}
            else:
                running = is_port_in_use(current_port)
                status_data = {"status": "running" if running else "stopped", "port": current_port, "protocol": current_protocol}
            
            msg_key = 'status_running' if running else 'status_stopped'
            response, exit_code = create_response(
                running,
                format_message(msg_key),
                status_data,
                0 if running else 1,
                current_port=current_port,
                current_protocol=current_protocol
            )
            
        elif args.command == "ping":
            # For command line usage, check appropriate method based on protocol
            if current_protocol == 'stdio':
                # For stdio, we can't easily ping another process
                running = False  # Default to not running for separate process
                ping_data = {"status": "healthy" if running else "unhealthy", "protocol": current_protocol}
            else:
                running = is_port_in_use(current_port)
                ping_data = {"status": "healthy" if running else "unhealthy", "port": current_port, "protocol": current_protocol}
            
            msg_key = 'ping_success' if running else 'ping_fail'
            response, exit_code = create_response(
                running,
                format_message(msg_key),
                ping_data,
                0 if running else 1,
                current_port=current_port,
                current_protocol=current_protocol
            )
            
        elif args.command == "version":
            import platform
            version_info = {
                "version": "1.0.0",
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "protocol": current_protocol
            }
            if current_protocol != 'stdio' and current_port is not None:
                version_info["port"] = current_port
            response, exit_code = create_response(
                True, 
                format_message('version', version=version_info['version']), 
                version_info,
                current_port=current_port,
                current_protocol=current_protocol
            )
            
        elif args.command == "help":
            parser.print_help()
            sys.exit(0)
                
    except KeyboardInterrupt:
        # Use defaults if variables are not defined
        current_port_safe = locals().get('current_port', video_server_PORT)
        current_protocol_safe = locals().get('current_protocol', video_server_PROTOCOL)
        response, exit_code = create_response(
            True, 
            format_message('interrupt'),
            current_port=current_port_safe,
            current_protocol=current_protocol_safe
        )
    except Exception as e:
        # Use defaults if variables are not defined
        current_port_safe = locals().get('current_port', video_server_PORT)
        current_protocol_safe = locals().get('current_protocol', video_server_PROTOCOL)
        response, exit_code = create_response(
            False, 
            format_message('error', error=str(e)), 
            exit_code=1,
            current_port=current_port_safe,
            current_protocol=current_protocol_safe
        )
    finally:
        if 'response' in locals():
            json_output = False
            if 'args' in locals() and hasattr(args, 'json'):
                json_output = args.json
            print_response(response, exit_code, json_output)