#!/bin/bash
# 创建全新虚拟环境的脚本 (Linux/Mac)

echo "========================================"
echo "  拼豆图案生成系统 - 环境设置"
echo "========================================"

# 检查Python
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "[错误] 未找到Python，请先安装Python 3.7+"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Python版本:"
$PYTHON_CMD --version
echo

# 创建虚拟环境
if [ -d "venv_desktop" ]; then
    echo "[警告] 虚拟环境已存在，将删除旧环境..."
    rm -rf venv_desktop
fi

echo ""
echo "[1/3] 创建虚拟环境..."
$PYTHON_CMD -m venv venv_desktop
if [ $? -ne 0 ]; then
    echo "[错误] 创建虚拟环境失败"
    exit 1
fi

echo "[成功] 虚拟环境创建完成"
echo ""

# 激活虚拟环境
echo "[2/3] 激活虚拟环境..."
source venv_desktop/bin/activate

# 升级pip
echo "[3/3] 升级pip到最新版本..."
python -m pip install --upgrade pip

echo ""
echo "========================================"
echo "  环境设置完成！"
echo "========================================"
echo ""
echo "现在运行以下命令安装依赖："
echo ""
echo "pip install -r requirements_desktop.txt"
echo ""
echo "或运行："
echo ""
echo "./run_desktop.sh"
echo ""
