@echo off
chcp 65001 >nul
echo 启动拼豆图案生成系统...
echo.

REM 尝试查找conda
set "CONDA_BAT="
if exist "%USERPROFILE%\anaconda3\Scripts\activate.bat" (
    set "CONDA_BAT=%USERPROFILE%\anaconda3\Scripts\activate.bat"
) else if exist "%USERPROFILE%\miniconda3\Scripts\activate.bat" (
    set "CONDA_BAT=%USERPROFILE%\miniconda3\Scripts\activate.bat"
) else if exist "C:\ProgramData\anaconda3\Scripts\activate.bat" (
    set "CONDA_BAT=C:\ProgramData\anaconda3\Scripts\activate.bat"
) else if exist "C:\ProgramData\miniconda3\Scripts\activate.bat" (
    set "CONDA_BAT=C:\ProgramData\miniconda3\Scripts\activate.bat"
) else if exist "C:\anaconda3\Scripts\activate.bat" (
    set "CONDA_BAT=C:\anaconda3\Scripts\activate.bat"
) else if exist "C:\miniconda3\Scripts\activate.bat" (
    set "CONDA_BAT=C:\miniconda3\Scripts\activate.bat"
) else if exist "F:\anaconda\Scripts\activate.bat" (
    set "CONDA_BAT=F:\anaconda\Scripts\activate.bat"
)

if "%CONDA_BAT%"=="" (
    echo 错误: 未找到conda，请使用PowerShell脚本运行
    echo 或者手动激活环境后运行: python app.py
    echo.
    echo 推荐: 右键 run.ps1 文件，选择"使用PowerShell运行"
    pause
    exit /b 1
)

echo 正在初始化conda环境...
call "%CONDA_BAT%"

echo.
echo 正在激活conda环境AAA...
call conda activate AAA
if errorlevel 1 (
    echo 错误: 无法激活conda环境AAA
    echo 请确保环境AAA已创建: conda create -n AAA python=3.7
    pause
    exit /b 1
)

echo.
echo 环境已激活，正在启动服务器...
echo 请在浏览器中访问 http://localhost:8000
echo.
python app.py
pause

