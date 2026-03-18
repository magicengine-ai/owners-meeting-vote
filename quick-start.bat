@echo off
chcp 65001 >nul
echo ============================================
echo 业主大会投票小程序 - 快速启动
echo ============================================
echo.

cd /d "%~dp0docker"

echo [1/4] 检查 Docker 安装...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker 未安装，请先安装 Docker Desktop
    echo 下载地址：https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo [OK] Docker 已安装
echo.

echo [2/4] 检查环境配置...
if not exist ".env" (
    echo [INFO] 复制环境配置文件...
    copy .env.example .env
    echo [SUCCESS] 已创建 .env 文件
    echo [INFO] 请编辑 .env 文件，填入正确的配置信息
    echo.
    pause
) else (
    echo [OK] 环境配置已存在
)
echo.

echo [3/4] 构建 Docker 镜像...
docker-compose build
if %errorlevel% neq 0 (
    echo [ERROR] 构建失败
    pause
    exit /b 1
)
echo [OK] 镜像构建完成
echo.

echo [4/4] 启动服务...
docker-compose up -d
if %errorlevel% neq 0 (
    echo [ERROR] 启动失败
    pause
    exit /b 1
)
echo.

echo ============================================
echo 部署完成！
echo ============================================
echo.
echo 服务访问地址:
echo   - 后端 API: http://localhost:8000
echo   - API 文档：http://localhost:8000/docs
echo   - 健康检查：http://localhost:8000/health
echo.
echo 常用命令:
echo   - 查看日志：docker-compose logs -f
echo   - 停止服务：docker-compose down
echo   - 重启服务：docker-compose restart
echo.
echo 按任意键查看服务状态...
pause >nul

docker-compose ps

echo.
echo 初始化数据库...
docker-compose exec -T backend alembic upgrade head

echo.
echo ============================================
echo 所有服务已启动！
echo ============================================
