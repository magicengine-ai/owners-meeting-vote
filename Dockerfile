# 微信云托管专用 Dockerfile
# 使用 Ubuntu 基础镜像（更容易获取）
FROM ubuntu:22.04

WORKDIR /app

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 配置 apt 使用阿里云镜像源
RUN sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list

# 安装 Python 和系统依赖
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建软链接
RUN ln -sf /usr/bin/python3.11 /usr/bin/python && \
    ln -sf /usr/bin/python3.11 /usr/bin/python3

# 安装 uvicorn
RUN pip3 install uvicorn -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制依赖文件并安装
COPY backend/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用代码
COPY backend/src ./src
COPY backend/main.py ./main.py

# 创建日志目录（云托管会自动收集 stdout/stderr）
RUN mkdir -p logs

# 暴露端口（微信云托管默认使用 8080 端口）
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 启动命令（微信云托管推荐端口 8080）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
