# 业主大会投票小程序 - 一键部署脚本
# 适用于 Windows PowerShell

param(
    [switch]$Docker,
    [switch]$Local,
    [switch]$Help
)

$ErrorActionPreference = "Stop"
$PROJECT_ROOT = "C:\Users\Admin\.openclaw\workspace\agents\engineer\projects\业主大会投票小程序"

function Write-Info {
    param($Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param($Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param($Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Show-Help {
    Write-Host @"
业主大会投票小程序 - 部署脚本

用法：
  .\deploy.ps1 [-Docker|-Local] [-Help]

选项:
  -Docker     使用 Docker 方式部署（推荐）
  -Local      使用本地 Python 方式部署
  -Help       显示此帮助信息

示例:
  .\deploy.ps1 -Docker     # 使用 Docker 部署
  .\deploy.ps1 -Local      # 使用本地部署
"@
}

function Check-Prerequisites-Docker {
    Write-Info "检查 Docker 安装..."
    
    try {
        $dockerVersion = docker --version
        Write-Success "Docker 已安装：$dockerVersion"
    } catch {
        Write-Error-Custom "Docker 未安装"
        Write-Info "请安装 Docker Desktop: https://www.docker.com/products/docker-desktop"
        exit 1
    }
    
    try {
        $composeVersion = docker-compose --version
        Write-Success "Docker Compose 已安装：$composeVersion"
    } catch {
        Write-Error-Custom "Docker Compose 未安装"
        exit 1
    }
}

function Check-Prerequisites-Local {
    Write-Info "检查本地环境..."
    
    # 检查 Python
    try {
        $pythonVersion = python --version
        Write-Success "Python 已安装：$pythonVersion"
    } catch {
        Write-Error-Custom "Python 未安装"
        Write-Info "请安装 Python 3.9+: https://www.python.org/downloads/"
        exit 1
    }
    
    # 检查 PostgreSQL
    try {
        $psqlVersion = psql --version
        Write-Success "PostgreSQL 已安装：$psqlVersion"
    } catch {
        Write-Error-Custom "PostgreSQL 未安装"
        Write-Info "请安装 PostgreSQL 14+: https://www.postgresql.org/download/"
        exit 1
    }
    
    # 检查 Redis
    try {
        $redisVersion = redis-cli --version
        Write-Success "Redis 已安装：$redisVersion"
    } catch {
        Write-Error-Custom "Redis 未安装"
        Write-Info "请安装 Redis: choco install redis-64"
        exit 1
    }
}

function Setup-Docker {
    Write-Info "开始 Docker 部署..."
    
    # 进入 docker 目录
    $dockerDir = Join-Path $PROJECT_ROOT "docker"
    Set-Location $dockerDir
    
    # 复制环境配置
    if (!(Test-Path ".env")) {
        Write-Info "复制环境配置文件..."
        Copy-Item ".env.example" ".env"
        Write-Success "环境配置已创建，请编辑 docker\.env 文件填入配置信息"
        
        # 生成 JWT_SECRET_KEY
        Write-Info "生成 JWT_SECRET_KEY..."
        $jwtKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
        
        # 更新 .env 文件
        $envContent = Get-Content ".env"
        $envContent = $envContent -replace "JWT_SECRET_KEY=.*", "JWT_SECRET_KEY=$jwtKey"
        $envContent | Set-Content ".env"
        Write-Success "JWT_SECRET_KEY 已生成"
    }
    
    # 构建镜像
    Write-Info "构建 Docker 镜像..."
    docker-compose build
    
    # 启动服务
    Write-Info "启动服务..."
    docker-compose up -d
    
    # 等待服务启动
    Write-Info "等待服务启动..."
    Start-Sleep -Seconds 10
    
    # 检查服务状态
    Write-Info "检查服务状态..."
    docker-compose ps
    
    # 初始化数据库
    Write-Info "初始化数据库..."
    docker-compose exec -T backend alembic upgrade head
    
    Write-Success "Docker 部署完成！"
    Write-Info @"

访问服务:
  - 后端 API: http://localhost:8000
  - API 文档：http://localhost:8000/docs
  - 健康检查：http://localhost:8000/health

常用命令:
  - 查看日志：docker-compose logs -f
  - 停止服务：docker-compose down
  - 重启服务：docker-compose restart
"@
}

function Setup-Local {
    Write-Info "开始本地部署..."
    
    # 进入后端目录
    $backendDir = Join-Path $PROJECT_ROOT "backend"
    Set-Location $backendDir
    
    # 创建虚拟环境
    if (!(Test-Path "venv")) {
        Write-Info "创建虚拟环境..."
        python -m venv venv
        Write-Success "虚拟环境已创建"
    }
    
    # 激活虚拟环境
    Write-Info "激活虚拟环境..."
    .\venv\Scripts\Activate.ps1
    
    # 安装依赖
    Write-Info "安装依赖..."
    pip install -r requirements.txt
    Write-Success "依赖已安装"
    
    # 创建 .env 文件
    if (!(Test-Path ".env")) {
        Write-Info "创建环境配置文件..."
        Copy-Item ".env.example" ".env"
        Write-Success "环境配置已创建，请编辑 backend\.env 文件"
    }
    
    # 初始化数据库
    Write-Info "初始化数据库..."
    Write-Info "请确保 PostgreSQL 已启动并创建数据库 vote_db"
    
    # 提示用户
    Write-Info @"

下一步操作:
1. 编辑 backend\.env 文件，填入配置信息
2. 在 PostgreSQL 中创建数据库：CREATE DATABASE vote_db;
3. 运行数据库迁移：alembic upgrade head
4. 启动服务：python main.py

访问服务:
  - 后端 API: http://localhost:8000
  - API 文档：http://localhost:8000/docs
"@
}

# 主程序
if ($Help) {
    Show-Help
    exit 0
}

if (!$Docker -and !$Local) {
    Write-Error-Custom "请指定部署方式：-Docker 或 -Local"
    Show-Help
    exit 1
}

Write-Info "业主大会投票小程序 - 部署脚本"
Write-Info "项目目录：$PROJECT_ROOT"

if ($Docker) {
    Check-Prerequisites-Docker
    Setup-Docker
} elseif ($Local) {
    Check-Prerequisites-Local
    Setup-Local
}

Write-Success "部署完成！"
