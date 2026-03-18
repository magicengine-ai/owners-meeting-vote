# 业主大会投票小程序 - 本地部署方案

## 📋 部署目标

在本地 Windows 环境部署业主大会投票小程序的后端服务器，用于开发和测试。

---

## 🚀 快速部署方案（推荐）

### 方案一：Docker 部署（最简单）⭐⭐⭐⭐⭐

**优点：** 一键部署、环境隔离、与生产环境一致

**前置要求：**
- Docker Desktop for Windows
- Git

**部署步骤：**

```powershell
# 1. 进入项目目录
cd C:\Users\Admin\.openclaw\workspace\agents\engineer\projects\业主大会投票小程序

# 2. 复制环境变量配置
cd docker
Copy-Item .env.example .env

# 3. 编辑 .env 文件（填入配置）
notepad .env

# 4. 启动所有服务
docker-compose up -d

# 5. 查看服务状态
docker-compose ps

# 6. 查看日志
docker-compose logs -f backend
```

**访问服务：**
- 后端 API: http://localhost:8000
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

**停止服务：**
```powershell
docker-compose down
```

---

### 方案二：本地 Python 部署

**优点：** 便于调试、开发

**前置要求：**
- Python 3.9+
- PostgreSQL 14+
- Redis 6+

**部署步骤：**

#### 1. 安装 PostgreSQL

```powershell
# 使用 Chocolatey 安装
choco install postgresql --version=14.0

# 或使用官方安装包
# https://www.postgresql.org/download/windows/
```

#### 2. 安装 Redis

```powershell
# 使用 Chocolatey 安装
choco install redis-64

# 启动 Redis 服务
redis-server --service-start
```

#### 3. 配置 Python 环境

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

#### 4. 配置环境变量

创建 `.env` 文件：

```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vote_db
DB_USER=postgres
DB_PASSWORD=your_password_here

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT 配置（生成随机密钥）
JWT_SECRET_KEY=your_jwt_secret_key_here

# 微信配置
WECHAT_APP_ID=wx0000000000000000
WECHAT_APP_SECRET=your_wechat_secret

# OCR 配置（百度 AI）
OCR_APP_ID=your_baidu_app_id
OCR_API_KEY=your_baidu_api_key
OCR_SECRET_KEY=your_baidu_secret_key

# 区块链配置
CHAIN_ENDPOINT=https://xchain.baidu.com
CHAIN_CHAIN_ID=your_chain_id

# 短信配置
SMS_PROVIDER=aliyun
SMS_ACCESS_KEY=your_sms_key
SMS_SECRET_KEY=your_sms_secret

# 开发环境配置
DEBUG=true
ENVIRONMENT=development
```

#### 5. 初始化数据库

```powershell
# 连接 PostgreSQL
psql -U postgres

# 创建数据库
CREATE DATABASE vote_db;
\q

# 运行数据库迁移
cd backend
alembic upgrade head
```

#### 6. 启动后端服务

```powershell
cd backend
python main.py
```

服务将在 `http://localhost:8000` 启动

---

## 🔧 环境配置详解

### 1. 生成 JWT_SECRET_KEY

```powershell
# 方法 1: 使用 OpenSSL
openssl rand -hex 32

# 方法 2: 使用 Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 方法 3: 使用 PowerShell
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

### 2. 微信小程序配置

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 注册小程序，获取 AppID 和 AppSecret
3. 配置服务器域名：
   - request: https://your-domain.com
   - uploadFile: https://your-domain.com
   - downloadFile: https://your-domain.com

### 3. 百度 OCR 配置

1. 登录 [百度 AI 开放平台](https://ai.baidu.com/)
2. 创建应用，获取 APP_ID、API_KEY、SECRET_KEY
3. 开通身份证识别服务

### 4. 区块链配置

1. 登录 [百度 X-Chains](https://xchain.baidu.com/)
2. 创建区块链
3. 获取 ChainID 和节点地址

---

## 📝 数据库初始化

### 创建管理员账户

```python
# scripts/create_admin.py
import sys
sys.path.insert(0, 'backend')

from sqlalchemy.orm import Session
from src.db import SessionLocal, engine, Base
from src.models import User
from src.auth.utils import get_password_hash
from datetime import datetime

def create_admin():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # 检查是否已有管理员
        admin = db.query(User).filter(User.openid == "admin_openid").first()
        if admin:
            print("⚠️  管理员已存在")
            return
        
        # 创建管理员
        admin = User(
            openid="admin_openid",
            nickname="管理员",
            phone="13800138000",
            is_verified=True,
            is_admin=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(admin)
        db.commit()
        
        print("✅ 管理员创建成功")
        print(f"   OpenID: admin_openid")
        print(f"   手机号：13800138000")
        
    except Exception as e:
        print(f"❌ 创建失败：{e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
```

运行：
```powershell
cd backend
python scripts/create_admin.py
```

---

## 🧪 测试验证

### 1. 健康检查

```powershell
curl http://localhost:8000/health
# 预期输出：{"status":"ok","version":"1.0.0"}
```

### 2. API 文档

访问：http://localhost:8000/docs

### 3. 测试登录接口

```powershell
curl -X POST http://localhost:8000/api/auth/wechat/login `
  -H "Content-Type: application/json" `
  -d '{\"code\":\"test_code\"}'
```

### 4. 查看日志

```powershell
# Docker 方式
docker-compose logs -f backend

# 本地方式
Get-Content backend\logs\app.log -Wait
```

---

## 🔍 常见问题

### 1. Docker 无法启动

```powershell
# 检查 Docker 是否运行
docker ps

# 重启 Docker Desktop
# 或重启服务
Restart-Service docker
```

### 2. PostgreSQL 连接失败

```powershell
# 检查 PostgreSQL 服务
Get-Service postgresql*

# 启动服务
Start-Service postgresql-x64-14

# 检查端口
netstat -ano | findstr :5432
```

### 3. Redis 连接失败

```powershell
# 检查 Redis 服务
Get-Service Redis

# 启动服务
redis-server --service-start

# 测试连接
redis-cli ping
# 应返回：PONG
```

### 4. 端口被占用

```powershell
# 查找占用端口的进程
netstat -ano | findstr :8000

# 结束进程
taskkill /F /PID <PID>
```

---

## 📊 性能优化

### 1. 数据库索引

```sql
-- 添加索引
CREATE INDEX IF NOT EXISTS idx_users_openid ON users(openid);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_vote_records_vote_id ON vote_records(vote_id);

-- 分析表
ANALYZE users;
ANALYZE vote_records;
```

### 2. Redis 缓存配置

```bash
# 配置 Redis 持久化
redis-cli CONFIG SET save "900 1 300 10 60 10000"

# 查看内存使用
redis-cli INFO memory
```

---

## 🔄 更新部署

### Docker 方式更新

```powershell
# 1. 拉取最新代码
cd C:\Users\Admin\.openclaw\workspace\agents\engineer\projects\业主大会投票小程序
git pull origin main

# 2. 重新构建并重启
cd docker
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 3. 运行数据库迁移
docker-compose exec backend alembic upgrade head

# 4. 验证
curl http://localhost:8000/health
```

### 本地方式更新

```powershell
# 1. 拉取最新代码
git pull origin main

# 2. 更新依赖
cd backend
pip install -r requirements.txt --upgrade

# 3. 运行数据库迁移
alembic upgrade head

# 4. 重启服务
# Ctrl+C 停止
python main.py  # 重新启动
```

---

## 🛡️ 安全建议

### 1. 修改默认密码

```sql
-- 修改数据库密码
ALTER USER postgres WITH PASSWORD 'new_strong_password';
```

### 2. 配置防火墙

```powershell
# 允许 PostgreSQL 端口
New-NetFirewallRule -DisplayName "PostgreSQL" -Direction Inbound -LocalPort 5432 -Protocol TCP -Action Allow

# 允许 Redis 端口
New-NetFirewallRule -DisplayName "Redis" -Direction Inbound -LocalPort 6379 -Protocol TCP -Action Allow
```

### 3. 定期备份

```powershell
# 数据库备份
pg_dump -U postgres vote_db > backup_$(Get-Date -Format "yyyyMMdd").sql

# Redis 备份
redis-cli BGSAVE
```

---

## 📞 技术支持

- **项目文档：** `./docs/`
- **API 文档：** http://localhost:8000/docs
- **GitHub:** https://github.com/magicengine-ai/owners-meeting-vote

---

**最后更新：** 2026-03-13  
**版本：** v1.0.0
