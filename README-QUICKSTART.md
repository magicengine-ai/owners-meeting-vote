# 业主大会投票小程序 - 快速启动指南

## 🚀 开发环境搭建

### 1. 前置要求

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- 微信小程序开发者工具

### 2. 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 复制环境配置
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# 编辑 .env 文件，配置数据库和第三方服务

# 启动数据库迁移
alembic upgrade head

# 启动后端服务
python main.py
```

后端服务将在 `http://localhost:8000` 启动

访问 API 文档：`http://localhost:8000/docs`

### 3. 前端启动

```bash
# 进入前端目录
cd frontend

# 使用微信小程序开发者工具打开项目
# 文件 -> 打开 -> 选择 frontend 目录

# 配置 AppID
# 项目详情 -> 基本配置 -> AppID

# 编译并运行
```

### 4. 数据库初始化

```bash
# 连接到 PostgreSQL
psql -U postgres

# 创建数据库
CREATE DATABASE vote_db;

# 退出
\q

# 运行数据库迁移
cd backend
alembic upgrade head
```

---

## 📝 开发流程

### 1. 创建新功能

```bash
# 创建功能分支
git checkout -b feature/xxx

# 开发功能
# ...

# 提交代码
git add .
git commit -m "feat: 实现 xxx 功能"

# 推送到远程
git push origin feature/xxx
```

### 2. 修复 Bug

```bash
# 创建修复分支
git checkout -b fix/xxx

# 修复问题
# ...

# 提交代码
git add .
git commit -m "fix: 修复 xxx 问题"

# 推送到远程
git push origin fix/xxx
```

---

## 🧪 测试

### 运行单元测试

```bash
cd backend
pytest tests/ -v --cov=src
```

### 运行集成测试

```bash
cd backend
pytest tests/integration/ -v
```

---

## 📦 部署

### 生产环境配置

1. 修改 `.env` 文件中的配置
2. 设置 `DEBUG=False`
3. 配置正确的数据库连接
4. 配置第三方服务密钥

### Docker 部署

```bash
# 构建镜像
docker build -t vote-app-backend:latest .

# 运行容器
docker run -d -p 8000:8000 --env-file .env vote-app-backend:latest
```

### 小程序发布

1. 在微信开发者工具中上传代码
2. 登录微信公众平台
3. 提交审核
4. 审核通过后发布

---

## 🔧 常见问题

### 1. 数据库连接失败

检查 PostgreSQL 是否运行：
```bash
# Windows
net start postgresql

# Linux
systemctl status postgresql
```

### 2. Redis 连接失败

检查 Redis 是否运行：
```bash
# Windows
redis-server

# Linux
systemctl status redis
```

### 3. 微信小程序无法请求后端

- 检查域名是否备案
- 检查是否配置 HTTPS
- 在微信公众平台配置合法域名

---

## 📞 技术支持

如有问题，请联系开发团队。

**最后更新：** 2026-03-11
