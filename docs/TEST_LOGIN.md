# 测试登录接口

## 启动后端服务

```bash
cd backend
python main.py
```

## 测试接口

### 1. 健康检查
```bash
curl http://localhost:8000/health
```

### 2. 发送短信验证码（开发环境）
```bash
curl -X POST http://localhost:8000/api/auth/phone/sms \
  -H "Content-Type: application/json" \
  -d '{"phone": "13800138000"}'
```

响应示例：
```json
{
  "sms_token": "abc123...",
  "expire_seconds": 300,
  "message": "验证码已发送"
}
```

**注意：** 开发环境下，验证码会打印在后端日志中！

### 3. 手机号登录
```bash
curl -X POST http://localhost:8000/api/auth/phone/login \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "13800138000",
    "sms_code": "123456",
    "sms_token": "abc123..."
  }'
```

响应示例：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "openid": "phone_xxx",
  "is_verified": false,
  "phone": "13800138000"
}
```

### 4. 微信登录（开发环境）
```bash
curl -X POST http://localhost:8000/api/auth/wechat/login \
  -H "Content-Type: application/json" \
  -d '{"code": "test_code_123"}'
```

### 5. 获取用户信息（需要 token）
```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## API 文档

启动服务后访问：http://localhost:8000/docs

## 注意事项

1. **开发环境配置**
   - 确保 `backend/.env` 文件中 `DEBUG = True`
   - 微信登录在开发环境会使用模拟 openid

2. **短信验证码**
   - 开发环境不会真正发送短信
   - 验证码会打印在后端日志中
   - 查看日志获取验证码

3. **数据库**
   - 确保 PostgreSQL 已启动
   - 创建数据库：`CREATE DATABASE vote_db;`
   - 或修改 `.env` 中的数据库配置

4. **依赖安装**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
