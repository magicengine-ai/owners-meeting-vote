# 业主大会投票小程序 - 环境安装指南

**适用系统：** Windows 10/11  
**更新时间：** 2026-03-13

---

## 📋 前置环境要求

项目需要以下软件：

| 软件 | 版本要求 | 用途 | 安装优先级 |
|------|---------|------|-----------|
| Python | 3.9+ | 后端运行环境 | ⭐⭐⭐⭐⭐ 必需 |
| PostgreSQL | 14+ | 数据库 | ⭐⭐⭐⭐⭐ 必需 |
| Redis | 6+ | 缓存 | ⭐⭐⭐⭐ 必需 |
| Docker Desktop | 最新 | 容器化部署（可选） | ⭐⭐⭐ 推荐 |
| Git | 最新 | 版本控制 | ⭐⭐⭐ 推荐 |

---

## 🚀 快速安装方案

### 方案一：使用 Chocolatey（推荐）⭐⭐⭐⭐⭐

Chocolatey 是 Windows 的包管理器，可以一键安装所有依赖。

#### 1. 安装 Chocolatey

以**管理员身份**打开 PowerShell：

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

验证安装：
```powershell
choco --version
```

#### 2. 一键安装所有依赖

以**管理员身份**打开 PowerShell 或 CMD：

```powershell
# 安装 Python
choco install python39 -y

# 安装 PostgreSQL
choco install postgresql14 -y

# 安装 Redis
choco install redis-64 -y

# 安装 Git（可选）
choco install git -y

# 安装 Docker Desktop（可选）
choco install docker-desktop -y
```

#### 3. 验证安装

```powershell
# 重启终端后执行
python --version
psql --version
redis-cli --version
git --version
docker --version
```

---

### 方案二：手动安装

#### 1. 安装 Python

**下载：** https://www.python.org/downloads/

**安装步骤：**
1. 下载 Python 3.9+ 安装包
2. 运行安装程序
3. ✅ **勾选"Add Python to PATH"**
4. 点击"Install Now"

**验证：**
```powershell
python --version
pip --version
```

#### 2. 安装 PostgreSQL

**下载：** https://www.postgresql.org/download/windows/

**安装步骤：**
1. 下载 PostgreSQL 14+ 安装包
2. 运行安装程序
3. 设置密码（记住这个密码！）
4. 保持默认端口：5432
5. 安装 pgAdmin（可选）

**验证：**
```powershell
# 需要添加到 PATH 或进入安装目录
& "C:\Program Files\PostgreSQL\14\bin\psql.exe" --version
```

**配置：**
```powershell
# 以管理员身份打开 CMD，启动服务
net start postgresql-x64-14

# 创建数据库
& "C:\Program Files\PostgreSQL\14\bin\psql.exe" -U postgres
# 输入密码后，执行：
CREATE DATABASE vote_db;
\q
```

#### 3. 安装 Redis

**下载：** https://github.com/microsoftarchive/redis/releases

**安装步骤：**
1. 下载 Redis-x64-3.0.504.msi（或更高版本）
2. 运行安装程序
3. 保持默认端口：6379

**验证：**
```powershell
# 启动 Redis
redis-server

# 新开一个终端测试
redis-cli ping
# 应返回：PONG
```

#### 4. 安装 Docker Desktop（可选）

**下载：** https://www.docker.com/products/docker-desktop/

**安装步骤：**
1. 下载 Docker Desktop
2. 运行安装程序
3. 重启电脑
4. 启动 Docker Desktop

**验证：**
```powershell
docker --version
docker-compose --version
```

---

## 🔧 项目依赖安装

### 1. 安装 Python 依赖

```powershell
# 进入后端目录
cd C:\Users\Admin\.openclaw\workspace\agents\engineer\projects\业主大会投票小程序\backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```powershell
# 复制环境配置
Copy-Item .env.example .env

# 编辑 .env 文件
notepad .env
```

**最小配置（开发环境）：**
```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vote_db
DB_USER=postgres
DB_PASSWORD=你的 PostgreSQL 密码

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT 配置（生成随机密钥）
JWT_SECRET_KEY=随机生成的密钥

# 开发环境
DEBUG=true
ENVIRONMENT=development

# 微信配置（开发可填测试值）
WECHAT_APP_ID=wx0000000000000000
WECHAT_APP_SECRET=test_secret

# OCR 配置（开发可跳过）
OCR_APP_ID=
OCR_API_KEY=
OCR_SECRET_KEY=
```

**生成 JWT_SECRET_KEY：**
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 📊 数据库初始化

### 方法一：使用 psql 命令行

```powershell
# 连接 PostgreSQL
& "C:\Program Files\PostgreSQL\14\bin\psql.exe" -U postgres

# 输入密码后，执行：
CREATE DATABASE vote_db;
\q
```

### 方法二：使用 pgAdmin

1. 打开 pgAdmin
2. 连接服务器（输入安装时设置的密码）
3. 右键"Databases" → "Create" → "Database"
4. 输入数据库名：`vote_db`
5. 点击"Save"

### 运行数据库迁移

```powershell
# 确保在 backend 目录，且已激活虚拟环境
cd backend
.\venv\Scripts\Activate.ps1

# 运行迁移
alembic upgrade head
```

---

## 🎯 启动服务

### 方式一：直接启动（开发推荐）

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python main.py
```

访问：http://localhost:8000

### 方式二：使用 Docker（生产推荐）

```powershell
cd docker
docker-compose up -d
```

---

## ✅ 验证安装

### 1. 检查所有服务

```powershell
# Python
python --version
# 应显示：Python 3.9.x 或更高

# PostgreSQL
& "C:\Program Files\PostgreSQL\14\bin\psql.exe" --version
# 应显示：psql (PostgreSQL) 14.x

# Redis
redis-cli --version
# 应显示：redis-cli 6.x

# 测试 Redis 连接
redis-cli ping
# 应返回：PONG

# 测试 PostgreSQL 连接
& "C:\Program Files\PostgreSQL\14\bin\psql.exe" -U postgres -c "SELECT version();"
# 应显示 PostgreSQL 版本信息
```

### 2. 测试后端服务

```powershell
# 启动后端后
curl http://localhost:8000/health
# 应返回：{"status":"ok","version":"1.0.0"}
```

### 3. 访问 API 文档

浏览器打开：http://localhost:8000/docs

---

## 🔍 常见问题

### 1. Python 无法识别

**问题：** `python` 命令无法识别

**解决：**
- 重新安装 Python，确保勾选"Add to PATH"
- 或手动添加环境变量：
  - 系统属性 → 高级 → 环境变量
  - 在 Path 中添加：`C:\Users\你的用户名\AppData\Local\Programs\Python\Python39\`
  - 和：`C:\Users\你的用户名\AppData\Local\Programs\Python\Python39\Scripts\`

### 2. PostgreSQL 服务未启动

**问题：** 无法连接数据库

**解决：**
```powershell
# 以管理员身份运行
net start postgresql-x64-14

# 或重启服务
net restart postgresql-x64-14
```

### 3. Redis 无法启动

**问题：** redis-server 闪退

**解决：**
```powershell
# 使用配置文件启动
redis-server redis.windows.conf

# 或安装为服务
redis-server --service-install
redis-server --service-start
```

### 4. 端口被占用

**问题：** 端口 8000/5432/6379 被占用

**解决：**
```powershell
# 查找占用端口的进程
netstat -ano | findstr :8000

# 结束进程
taskkill /F /PID 进程号
```

---

## 📝 安装检查清单

- [ ] Python 3.9+ 已安装
- [ ] PostgreSQL 14+ 已安装
- [ ] Redis 6+ 已安装
- [ ] 数据库 `vote_db` 已创建
- [ ] Python 虚拟环境已创建
- [ ] 依赖包已安装（pip install -r requirements.txt）
- [ ] .env 文件已配置
- [ ] 后端服务可以启动
- [ ] API 文档可以访问

---

## 🎯 下一步

安装完成后，参考以下文档：

1. **部署总结.md** - 完整的部署和使用指南
2. **LOCAL_DEPLOYMENT.md** - 本地部署详细步骤
3. **docs/DEPLOYMENT.md** - 生产环境部署指南

---

## 📞 技术支持

- **项目文档：** 查看项目根目录下的文档
- **API 文档：** http://localhost:8000/docs
- **GitHub:** https://github.com/magicengine-ai/owners-meeting-vote

---

**安装愉快！** 🎉

**最后更新：** 2026-03-13
