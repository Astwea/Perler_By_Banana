@echo off
chcp 65001 >nul
echo ========================================
echo   设置PowerShell执行策略
echo ========================================
echo.
echo 此脚本将允许在当前用户下运行PowerShell脚本
echo.
powershell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"
echo.
if errorlevel 1 (
    echo 设置失败，请手动执行：
    echo.
    echo powershell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
    echo.
) else (
    echo 设置成功！现在可以运行PowerShell脚本了
    echo.
)
pause

