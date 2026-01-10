# 拼豆图案生成系统启动脚本 (PowerShell)
Write-Host "启动拼豆图案生成系统..." -ForegroundColor Green
Write-Host ""

# 激活conda环境
Write-Host "正在激活conda环境AAA..." -ForegroundColor Yellow
& conda activate AAA

if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 无法激活conda环境AAA" -ForegroundColor Red
    Write-Host "请确保已安装Anaconda/Miniconda并正确配置环境变量" -ForegroundColor Yellow
    Read-Host "按回车键退出"
    exit 1
}

Write-Host ""
Write-Host "环境已激活，正在启动服务器..." -ForegroundColor Green
Write-Host "请在浏览器中访问 http://localhost:8000" -ForegroundColor Cyan
Write-Host ""

# 启动应用
python app.py

Read-Host "`n按回车键退出"

