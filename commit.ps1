# 业主大会投票小程序 - Git 提交脚本
# 使用方法：.\commit.ps1 "提交信息"

param(
    [string]$message = "feat: 项目初始化 - 基础框架搭建"
)

# 设置工作目录
$projectDir = "C:\Users\Admin\.openclaw\workspace\agents\engineer\projects\业主大会投票小程序"
Set-Location $projectDir

Write-Host "=== 业主大会投票小程序 - Git 提交 ===" -ForegroundColor Green
Write-Host "项目目录：$projectDir" -ForegroundColor Cyan
Write-Host ""

# 初始化 Git（如果未初始化）
if (-not (Test-Path ".git")) {
    Write-Host "初始化 Git 仓库..." -ForegroundColor Yellow
    git init
}

# 配置 Git 用户
git config user.email "admin@magicengine-ai.com"
git config user.name "magicengine-ai"

# 添加所有文件
Write-Host "添加文件到暂存区..." -ForegroundColor Yellow
git add .

# 显示状态
Write-Host ""
Write-Host "Git 状态:" -ForegroundColor Cyan
git status --short

# 提交
Write-Host ""
Write-Host "提交代码..." -ForegroundColor Yellow
git commit -m $message

# 显示提交日志
Write-Host ""
Write-Host "最近提交记录:" -ForegroundColor Cyan
git log --oneline -3

Write-Host ""
Write-Host "✅ 提交完成!" -ForegroundColor Green
