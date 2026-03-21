# Docker 镜像拉取 - 终极解决方案

## 🚨 当前问题

所有公共镜像源都失败了，需要使用更可靠的方法。

---

## ✅ 方案一：使用 GitHub Container Registry（推荐）

GHCR 在国内访问相对稳定。

### 步骤 1：拉取镜像

```powershell
# 使用 GHCR 镜像
docker pull ghcr.io/microsoft/python:3.11-slim
```

### 步骤 2：打标签

```powershell
docker tag ghcr.io/microsoft/python:3.11-slim python:3.11-slim
```

### 步骤 3：验证

```powershell
docker images | findstr python
```

---

## ✅ 方案二：使用 Docker 官方镜像（带签名）

### 步骤 1：配置不验证签名（临时）

编辑 Docker Desktop 配置：

```json
{
  "insecure-registries": [
    "registry-1.docker.io"
  ],
  "registry-mirrors": []
}
```

### 步骤 2：拉取镜像

```powershell
docker pull registry-1.docker.io/library/python:3.11-slim
```

---

## ✅ 方案三：手动下载镜像文件导入（最可靠）

### 步骤 1：下载镜像文件

访问以下网站下载 `.tar` 格式的镜像：

- https://hub.docker.com/layers/library/python/3.11-slim/images
- 或使用第三方：https://docker.1panel.live/

### 步骤 2：导入镜像

```powershell
# 假设下载到 python-3.11-slim.tar
docker load -i python-3.11-slim.tar
```

### 步骤 3：验证

```powershell
docker images | findstr python
```

---

## ✅ 方案四：使用替代基础镜像

如果 Python 官方镜像实在无法获取，可以使用其他基础镜像。

### 选项 A：使用 Ubuntu + Python

编辑 `cloud-deploy/Dockerfile.cloud`：

```dockerfile
# 使用 Ubuntu 镜像（可能更容易获取）
FROM ubuntu:22.04

WORKDIR /app

# 安装 Python
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    pip \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置 Python3 为默认
RUN ln -s /usr/bin/python3.11 /usr/bin/python

# 安装依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制代码
COPY backend/src ./src
COPY backend/main.py ./main.py

# 暴露端口
EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
```

### 选项 B：使用 Alpine + Python

```dockerfile
FROM python:3.11-alpine

WORKDIR /app

# 安装依赖
RUN apk add --no-cache \
    gcc \
    musl-dev \
    mariadb-dev \
    && rm -rf /var/cache/apk/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY backend/src ./src
COPY backend/main.py ./main.py

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
```

---

## ✅ 方案五：本地构建 Python 镜像（最后的手段）

### 步骤 1：创建 Dockerfile

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

CMD ["python3", "--version"]
```

### 步骤 2：构建镜像

```powershell
docker build -t python:3.11-slim -f Dockerfile.local .
```

---

## 🎯 推荐执行顺序

1. **先试方案一**：GHCR 镜像（最简单）
   ```powershell
   docker pull ghcr.io/microsoft/python:3.11-slim
   docker tag ghcr.io/microsoft/python:3.11-slim python:3.11-slim
   ```

2. **如果失败，试方案四**：使用 Ubuntu 基础镜像
   - 修改 Dockerfile
   - 重新构建

3. **最后手段**：方案三手动导入或方案五本地构建

---

## 📊 镜像大小对比

| 镜像 | 大小 | 推荐度 |
|------|------|--------|
| python:3.11-slim | ~120MB | ⭐⭐⭐⭐⭐ |
| python:3.11-alpine | ~50MB | ⭐⭐⭐⭐ |
| ubuntu:22.04 + Python | ~300MB | ⭐⭐⭐ |

---

## 🆘 如果所有方案都失败

可以考虑：
1. 使用朋友的电脑拉取镜像后导出
2. 使用云服务器构建镜像后推送
3. 使用微信云托管的代码包部署方式（不需要 Docker）

---

**先试试方案一（GHCR），如果不行再试方案四（Ubuntu 基础镜像）！**
