# Docker 镜像加速配置指南

## 🐳 问题说明

Docker Hub 官方镜像在国内下载速度慢或失败，需要配置镜像加速器。

---

## ✅ 解决方案

### 方案一：配置 Docker Desktop 镜像加速器（推荐）

#### Windows 配置方法

1. **打开 Docker Desktop**
   - 点击系统托盘中的 Docker 图标
   - 选择 **Dashboard** 或 **Settings**

2. **配置镜像加速器**
   - Settings → **Docker Engine**
   - 在 `registry-mirrors` 中添加以下加速器地址：

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ],
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false
}
```

3. **应用并重启**
   - 点击 **Apply & Restart**
   - 等待 Docker 重启完成

#### 验证配置

```powershell
docker info | findstr "Mirrors"
```

应该能看到配置的镜像加速器地址。

---

### 方案二：预拉取镜像（如果方案一无效）

在项目的父目录执行：

```powershell
# 手动拉取基础镜像（使用加速器）
docker pull registry.cn-hangzhou.aliyuncs.com/library/python:3.11-slim

# 打标签为官方镜像名
docker tag registry.cn-hangzhou.aliyuncs.com/library/python:3.11-slim python:3.11-slim
```

然后再运行部署脚本。

---

### 方案三：使用国内镜像仓库（备选）

如果 Docker Hub 完全无法访问，可以使用以下镜像：

```dockerfile
# 使用 DaoCloud 镜像
FROM docker.m.daocloud.io/python:3.11-slim

# 或使用网易云镜像
FROM hub-mirror.c.163.com/library/python:3.11-slim
```

修改 `cloud-deploy/Dockerfile.cloud` 中的第一行即可。

---

## 🔧 完整配置步骤

### 步骤 1：配置 Docker 镜像加速

按照方案一配置 Docker Desktop。

### 步骤 2：清理缓存（可选）

```powershell
# 清理构建缓存
docker builder prune -a -f

# 清理未使用的镜像
docker image prune -a -f
```

### 步骤 3：重新构建

```powershell
cd 业主大会投票小程序
.\cloud-deploy\deploy-to-cloud.ps1
```

选择 **选项 1**

---

## 📊 预期效果

### 配置前
```
Pulling python:3.11-slim...
[=================>                        ]  25% | ETA: 30min  (太慢！)
```

### 配置后
```
Pulling python:3.11-slim...
[========================================>] 100% | 2min  (很快！)
```

---

## 🆘 故障排查

### 问题 1：配置后仍然很慢

**检查：**
- Docker 是否已重启
- 镜像加速器地址是否正确
- 网络连接是否正常

**解决：**
```powershell
# 测试镜像加速器
curl https://docker.mirrors.ustc.edu.cn/version
```

### 问题 2：权限错误

**错误信息：**
```
pull access denied, repository does not exist
```

**解决：** 使用官方镜像 `python:3.11-slim`，不要使用阿里云镜像。

### 问题 3：磁盘空间不足

**检查：**
```powershell
docker system df
```

**清理：**
```powershell
docker system prune -a -f
```

---

## 📚 镜像加速器地址列表

| 服务商 | 地址 | 状态 |
|--------|------|------|
| 中科大 | https://docker.mirrors.ustc.edu.cn | ✅ 推荐 |
| 网易 | https://hub-mirror.c.163.com | ✅ |
| 百度 | https://mirror.baidubce.com | ✅ |
| DaoCloud | https://docker.m.daocloud.io | ⚠️ 需注册 |

---

## 💡 最佳实践

1. **优先使用官方镜像** + 镜像加速器
2. **定期清理缓存**，释放磁盘空间
3. **本地开发** 可以使用预构建的镜像
4. **CI/CD** 环境建议缓存基础镜像

---

**配置完成后，重新运行部署脚本即可！**

```powershell
.\cloud-deploy\deploy-to-cloud.ps1
```
