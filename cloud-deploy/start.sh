#!/bin/bash
# 微信云托管启动脚本

set -e

echo "🚀 启动业主大会投票小程序 API..."

# 打印环境信息（调试用）
echo "环境检查:"
echo "  - APP_VERSION: ${APP_VERSION:-'not set'}"
echo "  - DB_HOST: ${DB_HOST:-'not set'}"
echo "  - REDIS_HOST: ${REDIS_HOST:-'not set'}"
echo "  - 端口：${PORT:-8080}"

# 等待数据库就绪（如果有依赖）
if [ -n "$DB_HOST" ]; then
    echo "⏳ 等待数据库连接..."
    # 这里可以添加数据库连接检查逻辑
fi

# 启动应用（微信云托管推荐端口 8080）
echo "🎯 启动 Uvicorn 服务..."
exec uvicorn main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8080} \
    --workers ${WEB_CONCURRENCY:-2} \
    --access-log \
    --log-level info
