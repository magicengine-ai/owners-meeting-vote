# 业主大会投票小程序 - 云托管快速开始

> 📦 完整的部署指南请查看：`DEPLOYMENT.md`

---

## 🎯 三步部署

### 1️⃣ 开通微信云托管

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入小程序 -> **开发** -> **云托管**
3. 点击「开通云托管」
4. 创建 MySQL 数据库（2 核 4G 起步）
5. （可选）创建 Redis 数据库

---

### 2️⃣ 构建并部署

#### 方式 A：使用部署脚本（推荐）

```powershell
cd 业主大会投票小程序
.\cloud-deploy\deploy-to-cloud.ps1
```

按提示选择部署方式，脚本会自动完成构建。

#### 方式 B：手动构建 Docker 镜像

```bash
# 构建镜像
docker build -f cloud-deploy/Dockerfile.cloud -t vote-api:latest .

# 推送到腾讯云容器镜像服务
docker login ccr.ccs.tencentyun.com -u <用户名> -p <密码>
docker tag vote-api:latest ccr.ccs.tencentyun.com/<namespace>/vote-api:latest
docker push ccr.ccs.tencentyun.com/<namespace>/vote-api:latest
```

#### 方式 C：使用 CloudBase CLI

```bash
# 安装 CLI
npm install -g @cloudbase/cli

# 登录
cloudbase login

# 部署
cloudbase deploy -f cloudbaserc.json
```

---

### 3️⃣ 配置环境变量

在云托管控制台 -> **服务详情** -> **环境变量** 中添加：

```bash
# 必选配置
JWT_SECRET_KEY=<生成一个随机密钥>
WECHAT_APP_ID=<小程序 AppID>
WECHAT_APP_SECRET=<小程序 AppSecret>

# 可选配置（第三方服务）
OCR_APP_ID=<百度 OCR AppID>
OCR_API_KEY=<百度 OCR API Key>
SMS_ACCESS_KEY=<短信服务 Access Key>
```

> 💡 MySQL 和 Redis 的连接信息会自动注入，无需手动配置！

---

## 🔗 配置小程序域名

1. 微信公众平台 -> **开发** -> **开发设置**
2. 服务器域名配置：
   - **request 合法域名**：`https://<云托管服务域名>`
   - **uploadFile 合法域名**：`https://<云托管服务域名>`
   - **downloadFile 合法域名**：`https://<云托管服务域名>`

> 云托管服务域名格式：`https://<服务 ID>-<环境 ID>.service.tcloudbase.com`

---

## ✅ 验证部署

```bash
# 健康检查
curl https://<云托管服务域名>/health

# 预期返回
{"status": "ok", "version": "1.0.0"}
```

---

## 📊 服务配置建议

| 配置项 | 建议值 | 说明 |
|--------|--------|------|
| 最小实例数 | 0 | 夜间自动缩容，节省成本 |
| 最大实例数 | 10 | 根据流量调整 |
| CPU | 1 核 | 起步配置 |
| 内存 | 2048 MB | 起步配置 |
| 端口 | **8080** | 微信云托管默认端口 |
| 超时时间 | 30 秒 | 默认值 |

---

## 💰 成本估算

| 资源 | 配置 | 月费用 |
|------|------|--------|
| 云托管 | 按量计费 | ¥50-100 |
| MySQL | 2 核 4G | ¥200 |
| Redis | 1G | ¥100 |
| **合计** | - | **¥350-400** |

> 免费额度：50 万 CPU 秒/月，足够低频使用

---

## 🛠️ 常见问题

### 冷启动慢
设置最小实例数为 1-2，避免冷启动

### 数据库连接失败
- 检查是否在同一环境
- 确认环境变量已配置
- 检查数据库白名单

### 日志查看
云托管控制台 -> **服务详情** -> **日志查询**

---

## 📚 下一步

1. ✅ 完成部署
2. ⏭️ 配置小程序域名
3. ⏭️ 测试 API 接口
4. ⏭️ 上传小程序代码
5. ⏭️ 提交审核

---

**需要帮助？**

- 详细文档：`cloud-deploy/DEPLOYMENT.md`
- 官方文档：https://developers.weixin.qq.com/miniprogram/dev/wxcloud/guide/whitelist.html

**最后更新：** 2026-03-22
