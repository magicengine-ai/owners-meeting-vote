# 🚀 生产环境部署指南

**最后更新：** 2026-03-12  
**版本：** v1.0.0  
**状态：** ✅ 生产就绪

---

## 📋 部署前检查清单

### 1. 服务器准备

#### 硬件要求
- [x] CPU: 2 Core 或更高
- [x] 内存：4GB 或更高
- [x] 磁盘：50GB SSD 或更高
- [x] 网络：公网 IP，开放 80/443 端口

#### 系统要求
- [x] Ubuntu 20.04 LTS 或更高版本
- [x] Docker 20.10+
- [x] Docker Compose 2.0+
- [x] Git

#### 检查命令
```bash
# 检查系统版本
uname -a
cat /etc/os-release

# 检查 Docker
docker --version
docker-compose --version

# 检查资源
free -h
df -h
nproc
```

---

## 🔧 部署步骤

### 步骤 1：安装 Docker

```bash
# 1. 更新系统包
sudo apt update && sudo apt upgrade -y

# 2. 安装必要依赖
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 3. 添加 Docker GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 4. 添加 Docker 仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 5. 安装 Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# 6. 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 7. 验证安装
docker --version
docker-compose --version

# 8. 将当前用户加入 docker 组
sudo usermod -aG docker $USER
newgrp docker
```

---

### 步骤 2：克隆项目代码

```bash
# 1. 创建应用目录
sudo mkdir -p /opt/owners-meeting-vote
cd /opt/owners-meeting-vote

# 2. 克隆代码
sudo git clone git@github.com:magicengine-ai/owners-meeting-vote.git .
sudo chown -R $USER:$USER .

# 3. 验证代码
ls -la
# 应该看到：backend, frontend, docker, scripts, docs 等目录
```

---

### 步骤 3：配置环境变量

```bash
# 1. 复制环境配置文件
cp docker/.env.example docker/.env.production

# 2. 编辑环境变量
vim docker/.env.production
```

#### 必需配置项
```bash
# 数据库配置
DB_PASSWORD=your_strong_password_here

# JWT 配置（生成随机密钥）
JWT_SECRET_KEY=$(openssl rand -hex 32)

# 微信配置
WECHAT_APP_ID=wx0000000000000000
WECHAT_APP_SECRET=your_wechat_app_secret

# OCR 配置（百度 AI）
OCR_APP_ID=your_baidu_app_id
OCR_API_KEY=your_baidu_api_key
OCR_SECRET_KEY=your_baidu_secret_key

# 区块链配置
CHAIN_ENDPOINT=https://xchain.baidu.com
CHAIN_CHAIN_ID=your_chain_id

# 短信配置
SMS_PROVIDER=aliyun
SMS_ACCESS_KEY=your_sms_access_key
SMS_SECRET_KEY=your_sms_secret_key

# 生产环境配置
DEBUG=false
ENVIRONMENT=production
```

#### 生成 JWT_SECRET_KEY
```bash
# 方法 1：使用 openssl
openssl rand -hex 32

# 方法 2：使用 python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 方法 3：使用 /dev/urandom
head -c 32 /dev/urandom | xxd -p
```

---

### 步骤 4：配置 SSL 证书

```bash
# 1. 创建 SSL 目录
mkdir -p docker/ssl

# 2. 使用 Let's Encrypt 免费证书（推荐）
# 安装 certbot
sudo apt install -y certbot

# 3. 获取证书（需要域名）
sudo certbot certonly --standalone -d your-domain.com

# 4. 复制证书到项目目录
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docker/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem docker/ssl/key.pem

# 5. 设置权限
sudo chmod 600 docker/ssl/key.pem
sudo chmod 644 docker/ssl/cert.pem
```

#### 或使用自签名证书（仅测试）
```bash
# 生成自签名证书
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/ssl/key.pem \
  -out docker/ssl/cert.pem \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=YourOrg/CN=your-domain.com"
```

---

### 步骤 5：配置 Nginx

```bash
# 编辑 Nginx 配置
vim docker/nginx.conf
```

#### nginx.conf 配置示例
```nginx
events {
    worker_connections 1024;
}

http {
    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # 上游配置
    upstream backend {
        server backend:8000;
        keepalive 32;
    }

    # HTTP 重定向到 HTTPS
    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS 配置
    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL 证书
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # SSL 优化
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # 安全头
        add_header Strict-Transport-Security "max-age=31536000" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # 后端 API
        location /api/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # API 文档
        location /docs {
            proxy_pass http://backend/docs;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # 健康检查
        location /health {
            proxy_pass http://backend/health;
            access_log off;
        }

        # 根路径
        location / {
            proxy_pass http://backend/;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

---

### 步骤 6：启动服务

```bash
# 1. 进入 docker 目录
cd /opt/owners-meeting-vote/docker

# 2. 构建镜像
docker-compose build

# 3. 启动服务
docker-compose up -d

# 4. 查看服务状态
docker-compose ps

# 应该看到：
# NAME                STATUS              PORTS
# docker-backend-1    Up (healthy)        8000/tcp
# docker-db-1         Up (healthy)        5432/tcp
# docker-redis-1      Up (healthy)        6379/tcp
# docker-nginx-1      Up                  0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
```

---

### 步骤 7：数据库初始化

```bash
# 1. 等待数据库就绪
sleep 10

# 2. 创建数据库（如果未自动创建）
docker-compose exec db psql -U postgres -c "CREATE DATABASE vote_db;"

# 3. 运行数据库迁移
docker-compose exec backend alembic upgrade head

# 4. 创建管理员账户
docker-compose exec backend python3 scripts/create_admin.py

# 输入管理员信息：
# 用户名：admin
# 密码：your_admin_password
# 手机号：13800138000
```

#### 创建管理员脚本
```bash
# 创建脚本
cat > scripts/create_admin.py << 'EOF'
#!/usr/bin/env python3
"""
创建管理员账户
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        print(f"   密码：请联系开发者获取")
        
    except Exception as e:
        print(f"❌ 创建失败：{e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
EOF

chmod +x scripts/create_admin.py
```

---

### 步骤 8：验证部署

```bash
# 1. 健康检查
curl -k https://your-domain.com/health

# 预期输出：
# {"status":"ok","version":"1.0.0"}

# 2. 测试 API 文档
curl -k https://your-domain.com/docs

# 3. 测试登录接口
curl -X POST https://your-domain.com/api/auth/wechat/login \
  -H "Content-Type: application/json" \
  -d '{"code":"test_code"}'

# 4. 查看日志
docker-compose logs backend
docker-compose logs nginx

# 5. 检查数据库连接
docker-compose exec backend python3 -c "from src.db import SessionLocal; db = SessionLocal(); print('✅ 数据库连接成功')"
```

---

## 🔍 监控与日志

### 查看日志
```bash
# 实时查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f nginx
docker-compose logs -f db

# 查看最近 100 行
docker-compose logs --tail=100 backend

# 导出日志
docker-compose logs backend > backend.log
```

### 监控命令
```bash
# 查看容器状态
docker-compose ps

# 查看资源使用
docker stats

# 查看磁盘使用
docker system df

# 清理未使用的资源
docker system prune -a
```

---

## 🔄 更新部署

### 更新代码
```bash
# 1. 进入项目目录
cd /opt/owners-meeting-vote

# 2. 拉取最新代码
git pull origin main

# 3. 重新构建并重启
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 4. 运行迁移
docker-compose exec backend alembic upgrade head

# 5. 验证
curl -k https://your-domain.com/health
```

### 回滚版本
```bash
# 1. 回滚到上一个版本
git checkout HEAD~1

# 2. 重新部署
docker-compose down
docker-compose up -d

# 3. 回滚数据库迁移
docker-compose exec backend alembic downgrade -1
```

---

## 🛡️ 安全加固

### 1. 防火墙配置
```bash
# 安装 UFW
sudo apt install -y ufw

# 允许 SSH
sudo ufw allow 22/tcp

# 允许 HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status
```

### 2. 数据库安全
```bash
# 1. 修改默认密码
docker-compose exec db psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'new_strong_password';"

# 2. 限制远程访问（docker-compose.yml 已配置）
# 只允许容器内部访问

# 3. 定期备份
docker-compose exec db pg_dump -U postgres vote_db > backup_$(date +%Y%m%d).sql
```

### 3. 日志审计
```bash
# 1. 配置日志轮转
cat > /etc/logrotate.d/docker-containers << EOF
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    size=10M
    missingok
    delaycompress
    copytruncate
}
EOF

# 2. 监控异常登录
docker-compose logs backend | grep -i "failed\|error\|unauthorized"
```

---

## 📊 性能优化

### 1. 数据库优化
```sql
-- 添加索引
CREATE INDEX IF NOT EXISTS idx_users_openid ON users(openid);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_vote_records_vote_id ON vote_records(vote_id);
CREATE INDEX IF NOT EXISTS idx_meeting_attendees_meeting_id ON meeting_attendees(meeting_id);

-- 分析表
ANALYZE users;
ANALYZE vote_records;
ANALYZE meeting_attendees;
```

### 2. Redis 缓存
```bash
# 配置 Redis 持久化
docker-compose exec redis redis-cli CONFIG SET save "900 1 300 10 60 10000"

# 查看内存使用
docker-compose exec redis redis-cli INFO memory
```

### 3. Nginx 优化
```nginx
# 启用 Gzip 压缩
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_proxied expired no-cache no-store private auth;
gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml application/javascript;

# 连接优化
keepalive_timeout 65;
keepalive_requests 100;
```

---

## 🆘 故障排查

### 常见问题

#### 1. 服务无法启动
```bash
# 查看错误日志
docker-compose logs backend

# 检查端口占用
sudo netstat -tlnp | grep :8000

# 重启服务
docker-compose restart backend
```

#### 2. 数据库连接失败
```bash
# 检查数据库状态
docker-compose ps db

# 查看数据库日志
docker-compose logs db

# 测试连接
docker-compose exec backend python3 -c "from src.db import SessionLocal; db = SessionLocal(); print('OK')"
```

#### 3. SSL 证书问题
```bash
# 检查证书文件
ls -la docker/ssl/

# 验证证书
openssl x509 -in docker/ssl/cert.pem -text -noout

# 重启 Nginx
docker-compose restart nginx
```

#### 4. 内存不足
```bash
# 查看内存使用
free -h
docker stats

# 清理未使用的镜像
docker image prune -a

# 增加 Swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📞 技术支持

### 联系方式
- **GitHub Issues:** https://github.com/magicengine-ai/owners-meeting-vote/issues
- **邮箱:** support@example.com
- **电话:** 400-XXX-XXXX

### 文档
- **API 文档:** https://your-domain.com/docs
- **项目文档:** ./docs/
- **运维手册:** ./docs/OPERATIONS.md

---

**🎉 部署完成！祝使用愉快！**
