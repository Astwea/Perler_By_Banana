@echo off
chcp 65001 >nul
echo 手动启动脚本（直接使用当前环境）
echo.

echo 正在启动服务器...
echo 请在浏览器中访问 http://localhost:8000
echo.
echo 如果启动失败，请确保已安装依赖:
echo pip install -r requirements.txt
echo.

python app.py
pause
