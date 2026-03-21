# 🚀 立即部署 - 业主大会投票小程序

> ⏱️ **预计时间：15 分钟**  
> 📅 **最后更新：2026-03-22**  
> ✅ **状态：准备就绪，可立即部署**

---

## 📋 快速检查清单

开始前请确认：
- [ ] 已注册微信小程序账号
- [ ] 已获取小程序 AppID 和 AppSecret
- [ ] 已安装 Node.js 18+（用于 CloudBase CLI）
- [ ] 代码已推送到 GitHub ✅（已完成）

---

## 🎯 三步部署（推荐方式）

### 步骤 1️⃣：开通微信云托管（5 分钟）

1. **登录微信公众平台**
   ```
   https://mp.weixin.qq.com/
   ```

2. **开通云托管**
   - 左侧菜单：**开发** → **云托管**
   - 点击「开通云托管」
   - 选择环境（建议：生产环境）
   - 同意协议并开通

3. **创建 MySQL 数据库**
   - 云托管控制台 → **数据库** → **MySQL**
   - 点击「创建数据库」
   - 选择配置：**2 核 4G**（起步配置）
   - 设置账号密码（请妥善保管）
   - 等待创建完成（约 3-5 分钟）

---

### 步骤 2️⃣：部署服务（5 分钟）

#### 方式 A：使用部署脚本（最简单）

```powershell
# 1. 打开 PowerShell
cd C:\Users\Admin\.openclaw\workspace\agents\engineer\projects\业主大会投票小程序

# 2. 运行部署脚本
.\cloud-deploy\deploy-to-cloud.ps1
```

按提示操作：
- 选择 **1. Docker 镜像部署**
- 脚本会自动构建并推送镜像
- 在云托管控制台创建服务

#### 方式 B：使用 CloudBase CLI

```bash
# 1. 安装 CLI
npm install -g @cloudbase/cli

# 2. 登录
cloudbase login

# 3. 部署
cd 业主大会投票小程序
cloudbase deploy -f cloudbaserc.json
```

---

### 步骤 3️⃣：配置环境变量（3 分钟）

1. **进入云托管控制台**
   ```
   服务管理 → 点击刚创建的服务 → 环境变量
   ```

2. **添加以下变量**（点击「添加变量」）：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `APP_VERSION` | `1.0.0` | 版本号 |
| `DEBUG` | `false` | 生产环境关闭调试 |
| `PORT` | `8080` | **重要！** 云托管默认端口 |
| `JWT_SECRET_KEY` | `<随机密钥>` | 见下方生成方法 |
| `WECHAT_APP_ID` | `wx8888888888888888` | 你的小程序 AppID |
| `WECHAT_APP_SECRET` | `<小程序密钥>` | 微信公众平台获取 |

3. **生成 JWT_SECRET_KEY**

PowerShell 命令：
```powershell
[System.BitConverter]::ToString((New-Object Security.Cryptography.RNGCryptoServiceProvider).GetBytes(32)).Replace("-","")
```

复制生成的 64 位随机字符串作为密钥。

4. **保存并重启服务**
   - 点击「保存」
   - 服务会自动重启（约 1 分钟）

---

## ✅ 验证部署

### 1. 获取服务域名

云托管控制台 → **服务管理** → 复制服务域名
```
https://<服务 ID>-<环境 ID>.service.tcloudbase.com
```

### 2. 健康检查

浏览器访问或使用 curl：
```bash
curl https://<你的服务域名>/health
```

**预期返回：**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

### 3. 测试 API

```bash
# 根路径
curl https://<你的服务域名>/

# 预期返回
{
  "message": "欢迎使用业主大会投票小程序 API",
  "docs": "/docs",
  "health": "/health"
}
```

### 4. 查看日志

云托管控制台 → **服务详情** → **日志查询**

确认能看到请求日志。

---

## 🔗 配置小程序域名

### 重要！否则小程序无法调用 API

1. **登录微信公众平台**
   ```
   https://mp.weixin.qq.com/
   ```

2. **配置服务器域名**
   - 左侧菜单：**开发** → **开发设置**
   - 找到「服务器域名」
   - 点击「修改」

3. **添加以下域名**
   ```
   request 合法域名：
   https://<你的云托管服务域名>
   
   uploadFile 合法域名：
   https://<你的云托管服务域名>
   
   downloadFile 合法域名：
   https://<你的云托管服务域名>
   ```

4. **保存并等待生效**
   - 点击「保存并提交」
   - 等待 1-2 分钟生效

> ⚠️ 注意：每月只能修改 5 次，请谨慎操作

---

## 📱 小程序联调

### 修改前端配置

编辑文件：`frontend/utils/config.js`

```javascript
module.exports = {
  // 修改为你的云托管服务域名
  API_BASE_URL: 'https://<你的服务域名>',
  
  // 其他配置...
}
```

### 编译并测试

1. 打开微信开发者工具
2. 导入小程序项目（frontend 目录）
3. 编译并测试登录、投票等功能

---

## 🎉 部署完成！

现在你的小程序后端已经运行在微信云托管上了！

### 下一步

- [ ] 测试完整功能流程
- [ ] 配置百度 OCR（房产证识别）
- [ ] 配置短信服务（通知推送）
- [ ] 申请订阅消息模板
- [ ] 准备小程序审核材料

---

## 🆘 遇到问题？

### 常见问题速查

| 问题 | 解决方案 |
|------|----------|
| 健康检查失败 | 检查服务是否启动、端口是否为 8080 |
| 数据库连接失败 | 检查环境变量、数据库是否在同一环境 |
| CORS 错误 | 检查小程序域名配置 |
| 冷启动慢 | 设置最小实例数为 1-2 |

### 详细文档

- 📘 [完整部署操作手册](./cloud-deploy/部署操作手册.md)
- 📗 [微信云托管配置说明](./cloud-deploy/微信云托管配置说明.md)
- 📙 [GitHub Actions 自动部署](./.github/README-GitHub-Actions.md)
- 📕 [部署总结](./cloud-deploy/部署总结.md)

### 技术支持

- 官方文档：https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloudrun/src/
- 社区问答：https://developers.weixin.qq.com/community/develop/mixflow

---

## 📊 部署检查清单

完成后请勾选：

- [ ] ✅ 云托管已开通
- [ ] ✅ MySQL 数据库已创建
- [ ] ✅ 服务已部署
- [ ] ✅ 环境变量已配置
- [ ] ✅ 健康检查通过
- [ ] ✅ 小程序域名已配置
- [ ] ✅ 前端配置已更新
- [ ] ✅ 小程序测试通过

---

**祝部署顺利！🎉**

如有问题，请查看完整文档或联系技术支持。
