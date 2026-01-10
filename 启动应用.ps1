# 拼豆图案生成系统启动脚本 (PowerShell)
# 双击此文件或在PowerShell中运行: .\启动应用.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   拼豆图案生成系统" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查conda是否可用
$condaCmd = Get-Command conda -ErrorAction SilentlyContinue
if (-not $condaCmd) {
    Write-Host "错误: 未找到conda命令" -ForegroundColor Red
    Write-Host "请确保已安装Anaconda/Miniconda并正确配置环境变量" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "解决方法:" -ForegroundColor Yellow
    Write-Host "1. 检查Anaconda是否已安装" -ForegroundColor White
    Write-Host "2. 在Anaconda Prompt中运行此脚本" -ForegroundColor White
    Write-Host "3. 或者手动激活环境后运行: python app.py" -ForegroundColor White
    Read-Host "`n按回车键退出"
    exit 1
}

# 激活conda环境
Write-Host "正在激活conda环境 AAA..." -ForegroundColor Yellow
& conda activate AAA

if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 无法激活conda环境AAA" -ForegroundColor Red
    Write-Host ""
    Write-Host "解决方法:" -ForegroundColor Yellow
    Write-Host "1. 检查环境是否存在: conda env list" -ForegroundColor White
    Write-Host "2. 如果不存在，创建环境: conda create -n AAA python=3.7" -ForegroundColor White
    Read-Host "`n按回车键退出"
    exit 1
}

Write-Host "环境激活成功!" -ForegroundColor Green
Write-Host ""

# 验证Python环境
Write-Host "检查Python环境..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "Python版本: $pythonVersion" -ForegroundColor Cyan
Write-Host ""

# 检查依赖
Write-Host "检查依赖..." -ForegroundColor Yellow
try {
    python -c "import fastapi; import uvicorn; print('[OK] 核心依赖已安装')" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[警告] 某些依赖可能未安装" -ForegroundColor Yellow
        Write-Host "正在安装依赖..." -ForegroundColor Yellow
        pip install -r requirements.txt
    }
} catch {
    Write-Host "[警告] 无法检查依赖，将尝试安装" -ForegroundColor Yellow
    pip install -r requirements.txt
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   正在启动服务器..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "请在浏览器中访问: http://localhost:8000" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 停止服务器" -ForegroundColor Yellow
Write-Host ""

# 启动应用
python app.py

Write-Host ""
Read-Host "按回车键退出"

