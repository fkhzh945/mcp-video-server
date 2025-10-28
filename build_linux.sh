#!/bin/bash

# 视频服务器 MCP Server Linux 构建脚本
# 此脚本用于在Linux环境中构建独立可执行文件

echo "===== 视频服务器 MCP Server Linux 构建脚本 ====="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3。请先安装Python 3.8或更高版本。"
    exit 1
fi

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "错误: 未找到pip3。请先安装pip。"
    exit 1
fi

echo "正在创建虚拟环境..."
# 创建虚拟环境
python3 -m venv venv_linux

# 激活虚拟环境
source venv_linux/bin/activate

# 升级pip
echo "正在升级pip..."
pip install --upgrade pip

# 安装依赖
echo "正在安装项目依赖..."
pip install -r requirements.txt

# 确保pyinstaller已安装
echo "正在安装PyInstaller..."
pip install pyinstaller>=6.0.0

# 开始构建
echo "正在构建Linux可执行文件..."
pyinstaller video_server_server_linux.spec

# 检查构建结果
if [ $? -eq 0 ]; then
    echo "\n构建成功!"
    echo "可执行文件位置: ./dist/video_server-mcp-server"
    echo "\n使用方法:"
    echo "  ./dist/video_server-mcp-server start --port 5005"
    
    # 创建发行包
    echo "\n正在创建发行包..."
    mkdir -p release_linux
    cp dist/video_server-mcp-server release_linux/
    cp README.md release_linux/
    
    echo "发行包已创建在 ./release_linux 目录"
    echo "包含以下文件:"
    ls -la release_linux/
else
    echo "\n构建失败!"
    exit 1
fi

# 提示信息
echo "\n===== 构建完成 ====="
echo "注意: 此可执行文件只能在Linux环境下运行。"
echo "如果需要在Windows环境下运行，请使用 build.bat 或 build.ps1 脚本。"