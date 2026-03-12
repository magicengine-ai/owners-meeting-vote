#!/bin/bash

# 业主大会投票小程序 - 部署脚本

set -e

echo "🚀 开始部署..."

# 1. 拉取最新代码
echo "📦 拉取最新代码..."
git pull origin main

# 2. 构建 Docker 镜像
echo "🔨 构建 Docker 镜像..."
docker-compose -f docker/docker-compose.yml build

# 3. 启动服务
echo "▶️  启动服务..."
docker-compose -f docker/docker-compose.yml up -d

# 4. 等待服务就绪
echo "⏳ 等待服务就绪..."
sleep 10

# 5. 运行数据库迁移
echo "🗄️  运行数据库迁移..."
docker-compose -f docker/docker-compose.yml exec -T backend alembic upgrade head

# 6. 健康检查
echo "🏥 健康检查..."
for i in {1..10}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ 服务健康检查通过"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "❌ 服务健康检查失败"
        exit 1
    fi
    echo "等待中... ($i/10)"
    sleep 5
done

# 7. 查看日志
echo "📋 查看最新日志..."
docker-compose -f docker/docker-compose.yml logs --tail=20 backend

echo "🎉 部署完成！"
echo ""
echo "服务地址："
echo "  - API: http://localhost:8000"
echo "  - 文档：http://localhost:8000/docs"
echo "  - 健康检查：http://localhost:8000/health"
echo ""
echo "查看日志：docker-compose logs -f"
echo "停止服务：docker-compose down"
