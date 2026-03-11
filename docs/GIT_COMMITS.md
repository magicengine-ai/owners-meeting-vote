# 业主大会投票小程序 - Git 提交记录

## 提交历史

### 2026-03-11 18:50 - 项目初始化 ✅

**提交信息：**
```
feat: 项目初始化 - 业主大会投票小程序基础框架搭建

- 创建项目目录结构 (backend/frontend/docs)
- 实现 FastAPI 后端框架 (main.py, config.py, db.py)
- 设计数据库模型 (10 张表，94 个字段)
- 实现认证模块框架 (6 个接口)
- 实现投票模块框架 (6 个接口)
- 创建微信小程序前端 (首页完整实现)
- 编写完整 API 文档
- 编写开发计划和项目启动报告
- 配置 Git 版本控制
```

**提交文件：**
- README.md
- README-QUICKSTART.md
- .gitignore
- backend/main.py
- backend/requirements.txt
- backend/.env.example
- backend/src/config.py
- backend/src/db.py
- backend/src/models.py
- backend/src/auth/auth.py
- backend/src/vote/vote.py
- frontend/app.json
- frontend/app.js
- frontend/app.wxss
- frontend/project.config.json
- frontend/sitemap.json
- frontend/pages/index/index.js
- frontend/pages/index/index.wxml
- frontend/pages/index/index.wxss
- frontend/pages/index/index.json
- docs/API.md
- docs/DEVELOPMENT_PLAN.md
- docs/项目启动报告.md

**统计：**
- 文件数：23
- 代码行数：~2000+
- 文档字数：~15000+

---

## 待提交功能

### Week 1-2 完成后提交
```
feat: 实现 JWT 认证和登录流程

- 实现微信登录 API 对接
- 实现 JWT Token 生成和验证
- 实现用户信息管理
- 完成登录页面开发
- 完成认证页面开发
```

### Week 3-4 完成后提交
```
feat: 完成认证系统开发

- 对接百度 AI OCR 识别房产证
- 对接政府系统验证房产证
- 实现人脸识别功能
- 实现认证状态管理
- 实现认证审核后台
```

### Week 5-6 完成后提交
```
feat: 完成投票系统开发

- 实现完整投票流程
- 对接区块链平台存证
- 实现实时计票功能
- 实现委托投票功能
- 实现投票结果展示
```

### Week 7-8 完成后提交
```
feat: 完成会议系统开发

- 实现会议创建和管理
- 实现会议签到功能
- 实现会议通知推送
- 实现会议记录管理
```

### Week 9-10 完成后提交
```
feat: 测试完成和上线准备

- 完成单元测试
- 完成集成测试
- 完成性能测试
- 生产环境部署
- 小程序提交审核
```

---

## Git 使用规范

### 提交信息格式
```
<type>: <subject>

<body>
```

**type 类型：**
- feat: 新功能
- fix: Bug 修复
- docs: 文档更新
- style: 代码格式
- refactor: 重构
- test: 测试
- chore: 构建/工具

**示例：**
```
feat: 实现微信登录功能

- 对接微信 OAuth2.0
- 实现 JWT Token 生成
- 添加用户信息存储
```

### 分支管理

```bash
# 主分支
main

# 开发分支
develop

# 功能分支
feature/login
feature/vote
feature/meeting

# 修复分支
fix/ocr-issue
fix/auth-bug
```

---

**最后更新：** 2026-03-11
