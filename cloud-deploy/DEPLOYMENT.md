# 微信云托管部署指南

## 📋 部署前准备

### 1. 开通微信云托管
1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入小程序管理后台
3. 左侧菜单：**开发** -> **云托管**
4. 点击「开通云托管」，按指引完成开通

### 2. 创建云数据库（MySQL）
1. 云托管控制台 -> **数据库** -> **MySQL**
2. 点击「创建数据库」
3. 选择配置（建议：2 核 4G 起步）
4. 记录数据库连接信息（会自动注入环境变量）

### 3. 创建云数据库（Redis）（可选）
1. 云托管控制台 -> **数据库** -> **Redis**
2. 点击「创建数据库」
3. 选择配置（建议：1G 起步）

---

## 🚀 部署流程

### 方式一：使用微信开发者工具（推荐）

#### 步骤 1：安装 CLI 工具
```bash
npm install -g @cloudbase/cli
```

#### 步骤 2：登录微信云
```bash
cloudbase login
# 扫码登录
```

#### 步骤 3：初始化项目
```bash
cd 业主大会投票小程序
cloudbase init
# 选择已有环境或创建新环境
```

#### 步骤 4：部署服务
```bash
# 使用云托管配置文件
cloudbase deploy -f cloudbaserc.json
```

#### 步骤 5：查看部署状态
```bash
cloudbase status
```

---

### 方式二：使用 Docker 镜像部署

#### 步骤 1：构建镜像
```bash
cd 业主大会投票小程序
docker build -f cloud-deploy/Dockerfile.cloud -t vote-api:latest .
```

#### 步骤 2：推送镜像到腾讯云容器镜像服务
```bash
# 1. 登录腾讯云容器镜像服务
docker login ccr.ccs.tencentyun.com -u <用户名> -p <密码>

# 2. 打标签
docker tag vote-api:latest ccr.ccs.tencentyun.com/<namespace>/vote-api:latest

# 3. 推送
docker push ccr.ccs.tencentyun.com/<namespace>/vote-api:latest
```

#### 步骤 3：在云托管控制台部署
1. 云托管控制台 -> **服务管理** -> **新建服务**
2. 选择「自定义镜像」
3. 填写镜像地址：`ccr.ccs.tencentyun.com/<namespace>/vote-api:latest`
4. 配置环境变量（见下文）
5. 点击「部署」

---

## 🔧 环境变量配置

### 自动注入的环境变量（云托管自动提供）

部署 MySQL 和 Redis 后，以下环境变量会自动注入，无需手动配置：

```bash
# MySQL
TENCENTCLOUD_MYSQL_HOST
TENCENTCLOUD_MYSQL_PORT
TENCENTCLOUD_MYSQL_DATABASE
TENCENTCLOUD_MYSQL_USERNAME
TENCENTCLOUD_MYSQL_PASSWORD

# Redis
TENCENTCLOUD_REDIS_HOST
TENCENTCLOUD_REDIS_PORT
TENCENTCLOUD_REDIS_PASSWORD
```

### 需要手动配置的环境变量

在云托管控制台 -> **服务详情** -> **环境变量** 中添加：

```bash
# 应用配置
APP_VERSION=1.0.0
DEBUG=false
PORT=5000
WEB_CONCURRENCY=2

# JWT 配置（重要！请生成随机密钥）
JWT_SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080

# 微信配置
WECHAT_APP_ID=wx_xxxxxxxxxxxxxxxx
WECHAT_APP_SECRET=your-wechat-app-secret

# OCR 配置（百度 AI）
OCR_APP_ID=your-baidu-ocr-app-id
OCR_API_KEY=your-baidu-ocr-api-key
OCR_SECRET_KEY=your-baidu-ocr-secret-key

# 区块链配置
CHAIN_ENDPOINT=https://your-chain-endpoint.com
CHAIN_CHAIN_ID=your-chain-id

# 短信配置
SMS_PROVIDER=aliyun
SMS_ACCESS_KEY=your-sms-access-key
SMS_SECRET_KEY=your-sms-secret-key
SMS_SIGN_NAME=业主大会
```

---

## 📝 配置小程序服务器域名

1. 微信公众平台 -> **开发** -> **开发管理** -> **开发设置**
2. 服务器域名配置：
   - **request 合法域名**：`https://<云托管服务域名>`
   - **uploadFile 合法域名**：`https://<云托管服务域名>`
   - **downloadFile 合法域名**：`https://<云托管服务域名>`

> 云托管服务域名格式：`https://<服务 ID>-<环境 ID>.service.tcloudbase.com`

---

## 🧪 测试验证

### 1. 健康检查
```bash
curl https://<云托管服务域名>/health
# 预期返回：{"status": "ok", "version": "1.0.0"}
```

### 2. 测试 API
```bash
# 测试根路径
curl https://<云托管服务域名>/

# 测试认证接口
curl https://<云托管服务域名>/api/auth/health
```

### 3. 查看日志
- 云托管控制台 -> **服务详情** -> **日志查询**
- 或使用 CLI：`cloudbase logs <服务 ID>`

---

## ⚙️ 服务配置建议

### 扩缩容配置
```
最小实例数：0（夜间无流量时自动缩容，节省成本）
最大实例数：10（根据实际流量调整）
CPU：1 核
内存：2048 MB
超时时间：30 秒
```

### 自动扩缩容策略
- CPU 使用率 > 70% 时自动扩容
- CPU 使用率 < 30% 时自动缩容
- 冷启动时间：约 5-10 秒

---

## 🔐 安全建议

1. **关闭 DEBUG 模式**：生产环境务必设置 `DEBUG=false`
2. **使用 HTTPS**：云托管默认提供 HTTPS
3. **定期轮换密钥**：JWT_SECRET_KEY、微信 AppSecret 等
4. **配置访问日志**：开启云托管访问日志
5. **设置告警**：配置 CPU/内存/错误率告警

---

## 💰 成本估算

### 免费额度（每个小程序）
- 云托管：500,000 CPU 秒/月
- MySQL：740 小时/月
- Redis：740 小时/月

### 预计成本（按中等流量）
- 云托管：约 ¥50-100/月
- MySQL（2 核 4G）：约 ¥200/月
- Redis（1G）：约 ¥100/月
- **合计：约 ¥350-400/月**

> 实际成本根据流量波动，投票期间流量高峰可能增加

---

## 🛠️ 常见问题

### Q1: 冷启动慢怎么办？
- 设置最小实例数为 1-2，避免冷启动
- 优化代码启动速度，减少初始化耗时

### Q2: 数据库连接失败？
- 检查云托管和数据库是否在同一环境
- 确认环境变量是否正确注入
- 检查数据库白名单是否允许云托管访问

### Q3: 日志不输出？
- 确保使用 stdout/stderr 输出日志
- 云托管会自动收集，无需写入文件
- 检查日志级别设置

### Q4: 如何回滚版本？
- 云托管控制台 -> **版本管理** -> 选择历史版本 -> 点击「回滚」

---

## 📚 相关文档

- [微信云托管官方文档](https://developers.weixin.qq.com/miniprogram/dev/wxcloud/guide/whitelist.html)
- [云托管 CLI 工具](https://developers.weixin.qq.com/miniprogram/dev/wxcloud/guide/cloudbase/cli.html)
- [云托管最佳实践](https://developers.weixin.qq.com/miniprogram/dev/wxcloud/guide/best-practices.html)

---

**最后更新：** 2026-03-22  
**文档状态：** 已完成 ✅
