# GitHub Actions 自动部署配置说明

## ⚠️ 为什么需要手动配置？

GitHub 要求 Personal Access Token 必须具有 `workflow` 权限才能推送工作流文件。

如果你遇到以下错误：
```
refusing to allow a Personal Access Token to create or update workflow
```

请按以下步骤手动配置。

---

## 📋 配置步骤

### 步骤 1：在 GitHub 上创建 Workflow 文件

1. 访问仓库：https://github.com/magicengine-ai/owners-meeting-vote
2. 点击 **Actions** 标签
3. 点击 **set up a workflow yourself**
4. 复制以下内容并粘贴

### 步骤 2：复制 Workflow 配置

文件位置：`.github/workflows/deploy.yml`

```yaml
name: Deploy to WeChat Cloud Run

on:
  push:
    branches: [ main ]
    paths:
      - 'backend/**'
      - 'cloud-deploy/**'
      - 'cloudbaserc.json'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install CloudBase CLI
      run: npm install -g @cloudbase/cli
    
    - name: Login to CloudBase
      env:
        CLOUDBASE_API_KEY: ${{ secrets.CLOUDBASE_API_KEY }}
      run: |
        cloudbase login --apiKey $CLOUDBASE_API_KEY
    
    - name: Build Docker image
      run: |
        docker build -f cloud-deploy/Dockerfile.cloud \
          -t vote-api:${{ github.sha }} \
          .
    
    - name: Deploy to Cloud Run
      env:
        CLOUDBASE_ENV_ID: ${{ secrets.CLOUDBASE_ENV_ID }}
      run: |
        cloudbase deploy -f cloudbaserc.json \
          --env $CLOUDBASE_ENV_ID \
          --version ${{ github.sha }}
    
    - name: Notify success
      if: success()
      run: |
        echo "✅ 部署成功！"
        echo "版本：${{ github.sha }}"
        echo "时间：$(date)"
    
    - name: Notify failure
      if: failure()
      run: |
        echo "❌ 部署失败！"
        echo "请检查构建日志"
        exit 1
```

### 步骤 3：配置 GitHub Secrets

1. 进入仓库 **Settings**
2. 左侧菜单：**Secrets and variables** -> **Actions**
3. 点击 **New repository secret**

添加以下 Secrets：

| Secret 名称 | 值 | 获取方式 |
|------------|-----|----------|
| `CLOUDBASE_API_KEY` | xxx | 微信云托管控制台 -> 访问密钥 |
| `CLOUDBASE_ENV_ID` | env-xxx | 微信云托管控制台 -> 环境管理 |

### 步骤 4：获取云托管 API Key

1. 访问：https://cloud.weixin.qq.com/
2. 点击右上角头像 -> **访问密钥**
3. 点击「新建密钥」
4. 复制 API Key 到 GitHub Secrets

### 步骤 5：获取环境 ID

1. 微信云托管控制台 -> **环境管理**
2. 复制环境 ID（格式：`env-xxxxxxxx`）
3. 添加到 GitHub Secrets

---

## 🧪 测试部署

### 触发部署

推送代码到 main 分支：
```bash
git push origin main
```

### 查看部署状态

1. GitHub 仓库 -> **Actions** 标签
2. 点击最新的 workflow 运行
3. 查看构建和部署日志

### 部署成功标志

- ✅ Workflow 显示绿色勾
- ✅ 日志显示 "部署成功"
- ✅ 云托管控制台显示新版本
- ✅ 健康检查接口返回正常

---

## 🔧 替代方案：使用部署脚本

如果不想配置 GitHub Actions，可以使用本地部署脚本：

```powershell
cd 业主大会投票小程序
.\cloud-deploy\deploy-to-cloud.ps1
```

**对比：**

| 方式 | 优点 | 缺点 |
|------|------|------|
| GitHub Actions | 自动化、无需手动操作 | 需要配置 Secrets |
| 部署脚本 | 简单快速、一次配置 | 需要手动运行 |

**推荐：** 开发阶段用脚本，生产环境用 GitHub Actions

---

## 📞 故障排查

### 问题 1：Workflow 不触发

**检查：**
- 分支是否为 `main`
- 修改的文件是否在 `backend/**` 或 `cloud-deploy/**`
- Workflow 语法是否正确

### 问题 2：登录失败

**检查：**
- CLOUDBASE_API_KEY 是否正确
- API Key 是否已过期（需要重新生成）

### 问题 3：部署失败

**检查：**
- 环境 ID 是否正确
- 云托管服务是否已创建
- Docker 构建是否成功

---

## 📚 相关文档

- [部署操作手册](../cloud-deploy/部署操作手册.md)
- [快速开始](../cloud-deploy/README-云托管.md)
- [部署总结](../cloud-deploy/部署总结.md)

---

**最后更新：** 2026-03-22  
**状态：** 待手动配置 ⏳
