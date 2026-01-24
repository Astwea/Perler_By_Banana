#!/bin/bash
# 拼豆图案生成系统 - 桌面应用启动脚本 (Linux/Mac)

cd "$(dirname "$0")"

# 检查虚拟环境是否存在
if [ -d "venv_desktop/bin" ]; then
    echo "Activating virtual environment..."
    source venv_desktop/bin/activate
fi

# 运行应用
python desktop/main.py
