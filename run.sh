#!/bin/bash
echo "启动拼豆图案生成系统..."
echo ""
echo "正在检查依赖..."
pip install -r requirements.txt
echo ""
echo "启动服务器..."
python app.py

