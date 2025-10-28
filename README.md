# 视频服务器 MCP Server

## 项目概述

这是一个基于 Model Context Protocol (MCP) 的视频服务器，提供了视频设备管理、实时预览、录像回放等功能的标准化接口。服务器通过 HTTP 协议运行，集成了 API 密钥验证机制，确保接口调用的安全性。

## 核心功能

本服务器提供以下5个核心工具函数：

1. **设备管理**：获取视频设备列表、查询设备详细信息
2. **实时预览**：启动设备实时视频预览
3. **录像回放**：回放指定时间段的录像
4. **流地址获取**：获取设备的 RTSP/HTTP 视频流地址
5. **安全验证**：全接口 API 密钥验证保护

## API 密钥验证机制

服务器实现了严格的 API 密钥验证机制，确保只有授权的请求能够访问接口。

- **默认 API 密钥**：`mcp_video_api_key_2024`
- **支持多种验证方式**：
  - Authorization 头（Bearer 格式）
  - X-API-Key 头
  - API-Key 头
  - URL 查询参数 `api_key`

## 项目配置

- **服务器名称**：mcp-video-server
- **协议**：http
- **默认端口**：5005
- **模拟视频服务器地址**：http://localhost:8001
- **环境变量**：
  - `MCP_VIDEO_SERVER_PROTOCOL`：覆盖协议设置（stdio, sse, http）
  - `MCP_VIDEO_SERVER_PORT`：覆盖默认端口（仅用于 sse/http 协议）

## 快速开始

### 1. 环境设置

```powershell
# 安装依赖并激活虚拟环境
.\setup.ps1
```

### 2. 启动模拟视频服务器

```powershell
# 在独立终端启动模拟视频服务器
python mock_video_server.py
```

### 3. 启动 MCP 视频服务器

```powershell
# 启动服务器进行开发（使用 http 协议）
python server.py start --port 5005

# 检查状态
python server.py status --json

# 停止服务器
python server.py stop
```

## 工具函数详细说明

### 1. get_video_devices

获取视频设备列表，支持按设备类型、状态和关键词进行过滤。

**参数**：
- `device_type`：设备类型过滤（可选）
- `status`：设备状态过滤（可选）
- `keyword`：关键词搜索（可选）

**返回值**：包含设备列表和总数的字典

### 2. get_device_details

获取指定设备的详细信息。

**参数**：
- `device_id`：设备 ID（必需）

**返回值**：设备详细信息字典

### 3. start_live_preview

启动设备实时预览。

**参数**：
- `device_id`：设备 ID（必需）
- `stream_type`：流类型（main/sub，默认 main）

**返回值**：包含预览 URL 和状态信息的字典

### 4. playback_recording

回放指定设备在特定时间段的录像。

**参数**：
- `device_id`：设备 ID（必需）
- `start_time`：开始时间（ISO 格式，必需）
- `end_time`：结束时间（ISO 格式，必需）
- `stream_type`：流类型（main/sub，默认 main）

**返回值**：包含回放 URL 和状态信息的字典

### 5. get_stream_url

获取设备的视频流地址。

**参数**：
- `device_id`：设备 ID（必需）
- `protocol`：协议类型（rtsp/http，默认 rtsp）
- `stream_type`：流类型（main/sub，默认 main）

**返回值**：包含视频流地址和相关信息的字典

## API 使用示例

### 获取设备列表

```python
import requests

# 使用 Authorization 头
headers = {
    "Authorization": "Bearer mcp_video_api_key_2024"
}

response = requests.get("http://localhost:5005/api/tools/get_video_devices", headers=headers)
print(response.json())
```

### 获取流地址

```python
import requests

# 使用 X-API-Key 头
headers = {
    "X-API-Key": "mcp_video_api_key_2024"
}

params = {
    "device_id": "ca001",
    "protocol": "rtsp"
}

response = requests.get("http://localhost:5005/api/tools/get_stream_url", headers=headers, params=params)
print(response.json())
```

### 回放录像

```python
import requests

# 使用查询参数
params = {
    "device_id": "ca003",
    "start_time": "2024-01-14T00:00:00Z",
    "end_time": "2024-01-15T23:59:59Z",
    "api_key": "mcp_video_api_key_2024"
}

response = requests.get("http://localhost:5005/api/tools/playback_recording", params=params)
print(response.json())
```

## 命令行接口

服务器支持以下命令：

| 命令 | 描述 | 示例 |
|------|------|------|
| `start` | 启动服务器 | `python server.py start` |
| `start --protocol sse --port 8080` | 使用特定协议/端口启动 | `python server.py start --protocol sse --port 8080` |
| `stop` | 停止服务器（跨进程） | `python server.py stop` |
| `status` | 检查服务器状态 | `python server.py status --json` |
| `ping` | 健康检查 | `python server.py ping` |
| `version` | 显示版本信息 | `python server.py version --json` |
| `help` | 显示帮助信息 | `python server.py help` |

## 测试

### 运行测试脚本

```powershell
# 运行 API 测试
python test_api.py

# 运行服务器测试
python test_server.py

# 运行模拟服务器测试
python test_mock_server.py

# 运行视频 API 测试
python test_video_api.py
```

## 项目结构

```
mcp_video_server/
├── README.md                    # 项目文档
├── server.py                    # 主服务器实现
├── mock_video_server.py         # 模拟视频服务器
├── requirements.txt             # Python 依赖
├── test_api.py                  # API 测试脚本
├── test_server.py               # 服务器测试脚本
├── test_mock_server.py          # 模拟服务器测试脚本
├── test_video_api.py            # 视频 API 测试脚本
├── setup.ps1                    # 环境设置脚本
├── run.ps1                      # 快速运行脚本
├── manage-server.ps1            # 服务器管理脚本
├── build.ps1                    # PowerShell 构建脚本
├── build.bat                    # Windows 批处理构建脚本
└── video_server_server.spec     # PyInstaller 配置
```

## 生产部署

### 构建独立可执行文件

#### Windows 环境

```powershell
# 使用 PowerShell 构建（推荐）
.\build.ps1

# 或使用批处理脚本
.\build.bat
```

#### Linux 环境

```bash
# 赋予脚本执行权限
chmod +x build_linux.sh

# 运行构建脚本
./build_linux.sh
```

构建输出：
- Windows: `dist/video_server-mcp-server.exe`：独立可执行文件
- Linux: `dist/video_server-mcp-server`：独立可执行文件
- `build/`：构建产物和依赖

### 分发与运行

构建好的可执行文件可以在没有 Python 环境的系统上运行：

#### Windows 环境
```powershell
# 运行可执行文件
.\dist\video_server-mcp-server.exe start --port 5005
```

#### Linux 环境
```bash
# 运行可执行文件
./dist/video_server-mcp-server start --port 5005
```

### Docker容器化部署

#### 使用Docker Compose（推荐）

```bash
# 使用docker-compose构建和启动服务
docker-compose up -d --build
```

#### 使用Docker单独构建和运行

```bash
# 构建Docker镜像
docker build -t mcp-video-server .

# 运行Docker容器
docker run -d --name mcp-video-server -p 5005:5005 mcp-video-server
```

#### Docker环境变量配置

可以通过环境变量自定义服务配置：

```bash
docker run -d --name mcp-video-server \
  -p 5005:5005 \
  -e MCP_VIDEO_SERVER_PROTOCOL=http \
  -e MCP_VIDEO_SERVER_PORT=5005 \
  mcp-video-server
```

#### 容器日志查看

```bash
# 查看容器日志
docker logs mcp-video-server

# 实时查看日志
docker logs -f mcp-video-server
```

#### 停止和重启容器

```bash
# 停止容器
docker stop mcp-video-server

# 启动已停止的容器
docker start mcp-video-server

# 重启容器
docker restart mcp-video-server

# 使用docker-compose停止所有服务
docker-compose down
```

## 故障排除

### 常见问题

**API 密钥验证失败**：
- 确保提供了正确的 API 密钥 `mcp_video_api_key_2024`
- 检查密钥格式是否正确（Bearer 格式需要前缀）

**无法连接到模拟视频服务器**：
- 确保 `mock_video_server.py` 正在运行
- 检查端口 8001 是否被占用

**端口已被使用**：
```powershell
# 检查端口占用
netstat -ano | findstr 5005

# 终止占用进程
taskkill /F /PID <pid>
```

## 系统要求

- **开发环境**：Python 3.8+, PowerShell 5.0+
- **生产环境**：Windows/Linux（独立可执行文件）
- **依赖**：见 `requirements.txt`

## 第三方MCP对接信息

为方便第三方系统对接本视频服务器，以下是MCP服务器的配置信息：

```json
{
  "mcpServers": {
    "视频系统": {
      "url": "http://127.0.0.1:5005/mcp",
      "headers": {
        "Authorization": "Bearer mcp_video_api_rkey_2024"
      }
    }
  }
}
```

## 许可证

[MIT License](https://opensource.org/licenses/MIT)