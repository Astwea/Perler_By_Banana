@echo off
REM 创建全新虚拟环境的脚本

echo ========================================
echo   拼豆图案生成系统 - 环境设置
echo ========================================

REM 检查Python
python --version
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

REM 创建虚拟环境
if exist "venv_desktop" (
    echo [警告] 虚拟环境已存在，将删除旧环境...
    rmdir /s /q venv_desktop
)

echo.
echo [1/3] 创建虚拟环境...
python -m venv venv_desktop
if errorlevel 1 (
    echo [错误] 创建虚拟环境失败
    pause
    exit /b 1
)

echo [成功] 虚拟环境创建完成
echo.

REM 激活虚拟环境
echo [2/3] 激活虚拟环境...
call venv_desktop\Scripts\activate.bat

REM 升级pip
echo [3/3] 升级pip到最新版本...
python -m pip install --upgrade pip

echo.
echo ========================================
echo   环境设置完成！
echo ========================================
echo.
echo 现在运行以下命令安装依赖：
echo.
echo pip install -r requirements_desktop.txt
echo.
echo 或运行：
echo.
echo run_desktop.bat
echo.
pause
