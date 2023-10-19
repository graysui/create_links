#!/bin/bash

set -e

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    USE_SUDO="sudo"
else
    USE_SUDO=""
fi

# 检查Python3是否已经安装
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Installing..."
    $USE_SUDO apt update 2>&1
    $USE_SUDO apt install python3 -y 2>&1
fi

# 检查pip是否已经安装
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Installing..."
    $USE_SUDO apt install python3-pip -y 2>&1
fi

# 检查git是否已经安装
if ! command -v git &> /dev/null; then
    echo "git is not installed. Installing..."
    $USE_SUDO apt install git -y 2>&1
fi

# 克隆GitHub项目
if [ ! -d "create_links" ]; then
    git clone https://github.com/graysui/create_links.git 2>&1
fi

# 检查Python依赖库watchdog是否已经安装
if ! python3 -c "import watchdog" &> /dev/null 2>&1; then
    echo "watchdog library is not installed. Installing..."
    pip3 install --break-system-packages watchdog 2>&1
fi

# 获取当前路径（也就是脚本的安装位置）
INSTALL_PATH=$(pwd)

# 删除安装脚本
rm "$INSTALL_PATH/create_links/install_create_links.sh"

echo "============================================"
echo "请修改$INSTALL_PATH/create_links/config.ini配置文件"
echo "修改完成后，请执行以下步骤："
echo "1. cd $INSTALL_PATH/create_links"
echo "2. python3 create_links.py"
echo "============================================"
