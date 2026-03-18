# 业主大会投票小程序 - 环境安装脚本
# 请以管理员身份运行此脚本

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "业主大会投票小程序 - 环境安装" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[错误] 请以管理员身份运行此脚本！" -ForegroundColor Red
    Write-Host ""
    Write-Host "使用方法：" -ForegroundColor Yellow
    Write-Host "1. 右键点击 PowerShell" -ForegroundColor Yellow
    Write-Host "2. 选择'以管理员身份运行'" -ForegroundColor Yellow
    Write-Host "3. 运行此脚本：" -ForegroundColor Yellow
    Write-Host "   .\install-environment.ps1" -ForegroundColor Cyan
    Write-Host ""
    pause
    exit 1
}

Write-Host "[✓] 管理员权限确认" -ForegroundColor Green
Write-Host ""

# 安装 Chocolatey
Write-Host "[1/4] 正在安装 Chocolatey..." -ForegroundColor Cyan
try {
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    Write-Host "[✓] Chocolatey 安装成功" -ForegroundColor Green
} catch {
    Write-Host "[✗] Chocolatey 安装失败：$_" -ForegroundColor Red
    Write-Host "请检查网络连接后重试" -ForegroundColor Yellow
    pause
    exit 1
}
Write-Host ""

# 刷新环境变量
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# 安装 PostgreSQL
Write-Host "[2/4] 正在安装 PostgreSQL 14..." -ForegroundColor Cyan
try {
    choco install postgresql14 -y
    Write-Host "[✓] PostgreSQL 14 安装成功" -ForegroundColor Green
} catch {
    Write-Host "[✗] PostgreSQL 安装失败：$_" -ForegroundColor Red
    pause
    exit 1
}
Write-Host ""

# 安装 Redis
Write-Host "[3/4] 正在安装 Redis..." -ForegroundColor Cyan
try {
    choco install redis-64 -y
    Write-Host "[✓] Redis 安装成功" -ForegroundColor Green
} catch {
    Write-Host "[✗] Redis 安装失败：$_" -ForegroundColor Red
    pause
    exit 1
}
Write-Host ""

# 安装 Git（可选但推荐）
Write-Host "[4/4] 正在安装 Git..." -ForegroundColor Cyan
try {
    choco install git -y
    Write-Host "[✓] Git 安装成功" -ForegroundColor Green
} catch {
    Write-Host "[!] Git 安装失败（可选组件，可跳过）" -ForegroundColor Yellow
}
Write-Host ""

# 启动服务
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "正在启动服务..." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 启动 PostgreSQL
Write-Host "启动 PostgreSQL 服务..." -ForegroundColor Yellow
try {
    $pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
    if ($pgService) {
        Start-Service -Name $pgService.Name
        Write-Host "[✓] PostgreSQL 服务已启动：$($pgService.Name)" -ForegroundColor Green
    } else {
        Write-Host "[!] 未找到 PostgreSQL 服务，可能需要手动启动" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[!] PostgreSQL 服务启动失败：$_" -ForegroundColor Yellow
}
Write-Host ""

# 启动 Redis
Write-Host "启动 Redis 服务..." -ForegroundColor Yellow
try {
    $redisService = Get-Service -Name "Redis*" -ErrorAction SilentlyContinue
    if ($redisService) {
        Start-Service -Name $redisService.Name
        Write-Host "[✓] Redis 服务已启动：$($redisService.Name)" -ForegroundColor Green
    } else {
        Write-Host "[!] 未找到 Redis 服务，可能需要手动启动" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[!] Redis 服务启动失败：$_" -ForegroundColor Yellow
}
Write-Host ""

# 验证安装
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "验证安装..." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 验证 PostgreSQL
Write-Host "检查 PostgreSQL..." -ForegroundColor Yellow
try {
    $psqlPath = "C:\Program Files\PostgreSQL\14\bin\psql.exe"
    if (Test-Path $psqlPath) {
        $version = & $psqlPath --version
        Write-Host "[✓] $version" -ForegroundColor Green
    } else {
        Write-Host "[!] 未找到 psql.exe，请检查安装路径" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[!] PostgreSQL 验证失败：$_" -ForegroundColor Yellow
}
Write-Host ""

# 验证 Redis
Write-Host "检查 Redis..." -ForegroundColor Yellow
try {
    $redisVersion = redis-cli --version
    Write-Host "[✓] $redisVersion" -ForegroundColor Green
} catch {
    Write-Host "[!] Redis 验证失败，可能需要重启终端" -ForegroundColor Yellow
}
Write-Host ""

# 创建数据库
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "创建数据库..." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "创建 vote_db 数据库..." -ForegroundColor Yellow
try {
    $psqlPath = "C:\Program Files\PostgreSQL\14\bin\psql.exe"
    & $psqlPath -U postgres -c "CREATE DATABASE vote_db;" 2>$null
    if ($?) {
        Write-Host "[✓] 数据库 vote_db 创建成功" -ForegroundColor Green
    } else {
        Write-Host "[!] 数据库可能已存在或创建失败" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[!] 数据库创建失败：$_" -ForegroundColor Yellow
    Write-Host "可以稍后手动创建：" -ForegroundColor Cyan
    Write-Host "  psql -U postgres -c `"CREATE DATABASE vote_db;`"" -ForegroundColor Gray
}
Write-Host ""

# 完成提示
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "安装完成！" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "已安装的组件：" -ForegroundColor White
Write-Host "  ✓ Chocolatey (包管理器)" -ForegroundColor Green
Write-Host "  ✓ PostgreSQL 14 (数据库)" -ForegroundColor Green
Write-Host "  ✓ Redis 64 (缓存)" -ForegroundColor Green
Write-Host "  ✓ Git (版本控制)" -ForegroundColor Green
Write-Host ""
Write-Host "下一步操作：" -ForegroundColor Yellow
Write-Host "  1. 关闭当前终端窗口" -ForegroundColor Cyan
Write-Host "  2. 重新打开 PowerShell（不需要管理员权限）" -ForegroundColor Cyan
Write-Host "  3. 运行部署脚本：" -ForegroundColor Cyan
Write-Host "     cd C:\Users\Admin\.openclaw\workspace\agents\engineer\projects\业主大会投票小程序" -ForegroundColor Gray
Write-Host "     .\deploy.ps1 -Local" -ForegroundColor Gray
Write-Host ""
Write-Host "或参考文档：" -ForegroundColor Yellow
Write-Host "  README-部署说明.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
pause > $null
