# 微信云托管一键部署脚�?# 使用方法�?\cloud-deploy\deploy-to-cloud.ps1

param(
    [string]$EnvironmentId = "",
    [string]$ServiceName = "vote-api",
    [switch]$SkipBuild = $false
)

Write-Host "Deploying to WeChat Cloud Run..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 检�?Docker
$dockerVersion = docker --version 2>$null
if (-not $dockerVersion) {
    Write-Host "ERROR: Docker not found. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}
Write-Host "OK: Docker installed" -ForegroundColor Green

# 检�?Node.js
$nodeVersion = node --version 2>$null
if ($nodeVersion) {
    Write-Host "OK: Node.js $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "WARN: Node.js not found (optional, for CLI deploy)" -ForegroundColor Yellow
}

# 主菜�?Write-Host "`nPlease select deployment method:" -ForegroundColor White
Write-Host "  1. Docker image build (recommended)" -ForegroundColor White
Write-Host "  2. CloudBase CLI deploy" -ForegroundColor White
Write-Host "  3. Build Docker image only" -ForegroundColor White
Write-Host "  0. Exit" -ForegroundColor White

$choice = Read-Host "`nEnter choice (1/2/3/0)"

switch ($choice) {
    "1" {
        Write-Host "`nBuilding Docker image..." -ForegroundColor Yellow
        $dockerfilePath = Join-Path $PSScriptRoot "Dockerfile"
        $projectRoot = Split-Path $PSScriptRoot -Parent
        
        docker build -f $dockerfilePath -t vote-api:latest $projectRoot
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "OK: Docker image built successfully" -ForegroundColor Green
            Write-Host "`nNext steps:" -ForegroundColor Cyan
            Write-Host "  1. Push image to Tencent Container Registry"
            Write-Host "  2. Deploy to WeChat Cloud Run console"
            Write-Host "  3. Configure environment variables"
            Write-Host "`nSee cloud-deploy/DEPLOYMENT.md for details" -ForegroundColor Gray
        } else {
            Write-Host "ERROR: Docker build failed" -ForegroundColor Red
            exit 1
        }
    }
    
    "2" {
        Write-Host "`nDeploying with CloudBase CLI..." -ForegroundColor Yellow
        
        if (-not (cloudbase --version 2>$null)) {
            Write-Host "ERROR: CloudBase CLI not installed" -ForegroundColor Red
            Write-Host "Run: npm install -g @cloudbase/cli" -ForegroundColor Gray
            exit 1
        }
        
        if (-not $EnvironmentId) {
            $EnvironmentId = Read-Host "Enter environment ID"
        }
        
        $projectRoot = Split-Path $PSScriptRoot -Parent
        $cloudbasercPath = Join-Path $projectRoot "cloudbaserc.json"
        
        if (-not (Test-Path $cloudbasercPath)) {
            Write-Host "ERROR: cloudbaserc.json not found" -ForegroundColor Red
            exit 1
        }
        
        cloudbase deploy -f $cloudbasercPath --env $EnvironmentId
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "OK: Deployment successful" -ForegroundColor Green
        } else {
            Write-Host "ERROR: Deployment failed" -ForegroundColor Red
            exit 1
        }
    }
    
    "3" {
        Write-Host "`nBuilding Docker image only..." -ForegroundColor Yellow
        $dockerfilePath = Join-Path $PSScriptRoot "Dockerfile"
        $projectRoot = Split-Path $PSScriptRoot -Parent
        
        docker build -f $dockerfilePath -t vote-api:latest $projectRoot
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "OK: Docker image built" -ForegroundColor Green
        } else {
            Write-Host "ERROR: Docker build failed" -ForegroundColor Red
            exit 1
        }
    }
    
    "0" {
        Write-Host "Exit" -ForegroundColor Yellow
        exit 0
    }
    
    default {
        Write-Host "ERROR: Invalid choice" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Done!" -ForegroundColor Green
