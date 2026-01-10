@echo off
chcp 65001 >nul
echo ========================================
echo   拼豆图案生成系统 - 快速启动
echo ========================================
echo.
echo 正在尝试使用PowerShell启动...
echo.

REM 尝试直接使用PowerShell运行启动脚本
powershell -ExecutionPolicy Bypass -File "启动应用.ps1"

if errorlevel 1 (
    echo.
    echo PowerShell启动失败，尝试使用CMD方式...
    echo.
    call run.bat
)

pause

