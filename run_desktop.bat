@echo off
REM 拼豆图案生成系统 - 桌面应用启动脚本

cd /d "%~dp0"

REM 检查虚拟环境是否存在
if exist "venv_desktop\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv_desktop\Scripts\activate.bat
)

REM 运行应用
python desktop\main.py

pause
