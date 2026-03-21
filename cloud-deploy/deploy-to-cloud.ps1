# 微信云托管一键部署脚本
# 使用方法：.\cloud-deploy\deploy-to-cloud.ps1

param(
    [string]$EnvironmentId = "",
    [string]$ServiceName = "vote-api",
    [switch]$SkipBuild = $false
)

Write-Host "🚀 业主大会投票小程序 - 微信云托管部署" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 检查必要工具
function Check-Prerequisites {
    Write-Host "`n📦 检查环境..." -ForegroundColor Yellow
    
    # 检查 Docker
    $dockerVersion = docker --version 2>$null
    if (-not $dockerVersion) {
        Write-Host "❌ 未检测到 Docker，请先安装 Docker Desktop" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Docker: $dockerVersion" -ForegroundColor Green
    
    # 检查 Node.js
    $nodeVersion = node --version 2>$null
    if (-not $nodeVersion) {
        Write-Host "⚠️  未检测到 Node.js（可选，用于 CLI 部署）" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
    }
    
    # 检查 @cloudbase/cli
    $cloudbaseVersion = cloudbase --version 2>$null
    if (-not $cloudbaseVersion) {
        Write-Host "⚠️  未安装 CloudBase CLI，建议使用 Docker 方式部署" -ForegroundColor Yellow
        Write-Host "   安装命令：npm install -g @cloudbase/cli" -ForegroundColor Gray
    } else {
        Write-Host "✅ CloudBase CLI: $cloudbaseVersion" -ForegroundColor Green
    }
}

# 构建 Docker 镜像
function Build-DockerImage {
    param([string]$ImageTag = "vote-api:latest")
    
    Write-Host "`n🔨 构建 Docker 镜像..." -ForegroundColor Yellow
    Write-Host "   镜像标签：$ImageTag" -ForegroundColor Gray
    
    $dockerfilePath = Join-Path $PSScriptRoot "Dockerfile.cloud"
    $projectRoot = Split-Path $PSScriptRoot -Parent
    
    docker build -f $dockerfilePath -t $ImageTag $projectRoot
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker 构建失败" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Docker 镜像构建成功" -ForegroundColor Green
}

# 推送镜像到腾讯云
function Push-DockerImage {
    param(
        [string]$ImageTag,
        [string]$RegistryUrl,
        [string]$Namespace,
        [string]$Username,
        [string]$Password
    )
    
    Write-Host "`n📤 推送镜像到腾讯云容器镜像服务..." -ForegroundColor Yellow
    
    $targetTag = "$RegistryUrl/$Namespace/vote-api:latest"
    
    # 登录
    Write-Host "   登录容器镜像服务..." -ForegroundColor Gray
    docker login $RegistryUrl -u $Username -p $Password 2>$null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 登录失败，请检查账号密码" -ForegroundColor Red
        exit 1
    }
    
    # 打标签
    Write-Host "   打标签：$targetTag" -ForegroundColor Gray
    docker tag $ImageTag $targetTag
    
    # 推送
    Write-Host "   推送中..." -ForegroundColor Gray
    docker push $targetTag
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 推送失败" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ 镜像推送成功" -ForegroundColor Green
    Write-Host "   镜像地址：$targetTag" -ForegroundColor Cyan
}

# 使用 CLI 部署
function Deploy-WithCLI {
    param([string]$EnvironmentId)
    
    Write-Host "`n☁️  使用 CloudBase CLI 部署..." -ForegroundColor Yellow
    
    if (-not (cloudbase --version 2>$null)) {
        Write-Host "❌ 未安装 CloudBase CLI" -ForegroundColor Red
        Write-Host "   请先运行：npm install -g @cloudbase/cli" -ForegroundColor Gray
        exit 1
    }
    
    # 检查登录状态
    Write-Host "   检查登录状态..." -ForegroundColor Gray
    cloudbase login 2>$null
    
    # 部署
    $projectRoot = Split-Path $PSScriptRoot -Parent
    $cloudbasercPath = Join-Path $projectRoot "cloudbaserc.json"
    
    if (-not (Test-Path $cloudbasercPath)) {
        Write-Host "❌ 未找到 cloudbaserc.json" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "   开始部署..." -ForegroundColor Gray
    cloudbase deploy -f $cloudbasercPath --env $EnvironmentId
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 部署失败" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ 部署成功" -ForegroundColor Green
}

# 主流程
function Main {
    Check-Prerequisites
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "请选择部署方式:" -ForegroundColor White
    Write-Host "  1. Docker 镜像部署（推荐）" -ForegroundColor White
    Write-Host "  2. CloudBase CLI 部署" -ForegroundColor White
    Write-Host "  3. 仅构建 Docker 镜像（不部署）" -ForegroundColor White
    Write-Host "  0. 退出" -ForegroundColor White
    
    $choice = Read-Host "`n请输入选项 (1/2/3/0)"
    
    switch ($choice) {
        "1" {
            # Docker 镜像部署
            $imageTag = "vote-api:latest"
            
            if (-not $SkipBuild) {
                Build-DockerImage -ImageTag $imageTag
            }
            
            Write-Host "`n📋 接下来需要手动操作:" -ForegroundColor Cyan
            Write-Host "  1. 登录腾讯云容器镜像服务" -ForegroundColor White
            Write-Host "     https://console.cloud.tencent.com/tcr" -ForegroundColor Gray
            Write-Host "  2. 创建命名空间（如果没有）" -ForegroundColor White
            Write-Host "  3. 推送镜像（脚本可自动完成，需要账号信息）" -ForegroundColor White
            Write-Host "  4. 在云托管控制台部署服务" -ForegroundColor White
            Write-Host "     https://console.cloud.tencent.com/tcb" -ForegroundColor Gray
            
            $autoPush = Read-Host "`n是否自动推送镜像？(y/n)"
            if ($autoPush -eq "y" -or $autoPush -eq "Y") {
                $registryUrl = Read-Host "请输入容器镜像服务地址 (如 ccr.ccs.tencentyun.com)"
                $namespace = Read-Host "请输入命名空间"
                $username = Read-Host "请输入用户名"
                $password = Read-Host "请输入密码" -AsSecureString
                $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
                $plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
                
                Push-DockerImage -ImageTag $imageTag -RegistryUrl $registryUrl -Namespace $namespace -Username $username -Password $plainPassword
            }
        }
        
        "2" {
            # CLI 部署
            if (-not $EnvironmentId) {
                $EnvironmentId = Read-Host "请输入环境 ID"
            }
            Deploy-WithCLI -EnvironmentId $EnvironmentId
        }
        
        "3" {
            # 仅构建
            Build-DockerImage -ImageTag "vote-api:latest"
        }
        
        "0" {
            Write-Host "👋 已取消部署" -ForegroundColor Yellow
            exit 0
        }
        
        default {
            Write-Host "❌ 无效选项" -ForegroundColor Red
            exit 1
        }
    }
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "✅ 部署流程完成！" -ForegroundColor Green
    Write-Host "`n📝 下一步:" -ForegroundColor Cyan
    Write-Host "  1. 在云托管控制台配置环境变量" -ForegroundColor White
    Write-Host "  2. 在小程序后台配置服务器域名" -ForegroundColor White
    Write-Host "  3. 测试 API 接口" -ForegroundColor White
    Write-Host "`n📚 详细文档：cloud-deploy/DEPLOYMENT.md" -ForegroundColor Gray
}

# 执行主流程
Main
