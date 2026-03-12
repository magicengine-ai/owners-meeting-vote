# 用户中心页面实现说明

**完成时间：** 2026-03-12 23:00  
**状态：** ✅ 已完成

---

## 📋 实现内容

### 1️⃣ 个人中心页面

#### 页面路径
`/pages/profile/profile`

#### 核心功能

✅ **用户信息展示**
- 头像/默认头像
- 昵称
- 手机号
- OpenID（未设置昵称时）

✅ **认证状态卡片**
- 已认证 ✅（绿色）
- 审核中 ⏳（黄色，带脉冲动画）
- 未认证/认证失败 ⚠️（红色）
- 点击跳转到认证页面

✅ **功能菜单**
- 🗳️ 我的投票（带数量徽章）
- 📋 我的会议（带数量徽章）
- 🏠 我的房产（显示房产地址预览）
- 🔔 消息通知（带数量徽章）

✅ **设置菜单**
- ℹ️ 关于我们
- ❓ 帮助与反馈

✅ **退出登录**
- 确认对话框
- 清除 Token
- 跳转登录页

#### 文件结构

```
frontend/pages/profile/
├── profile.js       # 页面逻辑
├── profile.wxml     # 页面结构
├── profile.wxss     # 页面样式
└── profile.json     # 页面配置
```

---

### 2️⃣ 房产详情页面

#### 页面路径
`/pages/profile/property/property`

#### 核心功能

✅ **房产信息卡片**
- 产权人姓名
- 房产证号
- 房屋地址
- 建筑面积
- 认证状态
- 认证时间

✅ **投票权信息**
- 投票权数（根据面积计算）
- 投票权比例
- 计算规则说明

✅ **状态展示**
- 已认证：显示完整信息
- 未认证：显示空状态和去认证按钮
- 认证失败：显示重新认证按钮

#### 文件结构

```
frontend/pages/profile/property/
├── property.js
├── property.wxml
├── property.wxss
└── property.json
```

---

## 🎨 UI 设计特点

### 1. 用户信息卡片
- 渐变背景（紫蓝色）
- 大头像（120rpx）
- 白色文字
- 认证状态徽章

### 2. 认证状态徽章
```css
已认证：绿色背景 #07c160
审核中：黄色背景 #ff9500（脉冲动画）
未认证：红色背景 #ff4444
```

### 3. 功能菜单
- 白色卡片
- Emoji 图标
- 右箭头指示
- 数字徽章（红底白字）
- 按压反馈效果

### 4. 房产信息
- 信息列表布局
- 标签 + 内容
- 状态颜色区分
- 空状态引导

---

## 🚀 使用流程

### 用户中心访问流程

```
1. 点击 TabBar"我的"
   ↓
2. 显示用户信息卡片
   ↓
3. 查看认证状态
   ↓
4. 点击功能菜单
   ↓
5. 跳转到对应页面
```

### 认证状态流转

```
未认证 → 点击去认证 → 上传房产证 → 审核中
                                     ↓
                                 审核通过 → 已认证
                                     ↓
                                 审核失败 → 重新认证
```

---

## 📝 接口说明

### 已用接口

| 接口 | 方法 | 用途 |
|------|------|------|
| `/api/auth/me` | GET | 获取用户信息 |
| `/api/auth/verify/status` | GET | 查询认证状态 |

### 待实现接口

| 接口 | 方法 | 用途 |
|------|------|------|
| `/api/user/property` | GET | 获取房产详细信息 |
| `/api/user/votes` | GET | 获取用户投票列表 |
| `/api/user/meetings` | GET | 获取用户会议列表 |
| `/api/user/notices` | GET | 获取用户通知列表 |

---

## 🔧 配置说明

### 页面路由

在 `app.json` 中添加：

```json
{
  "pages": [
    "pages/index/index",
    "pages/profile/profile",
    "pages/profile/property/property"
  ]
}
```

### TabBar 配置

```json
{
  "tabBar": {
    "list": [
      {
        "pagePath": "pages/profile/profile",
        "text": "我的",
        "iconPath": "images/profile.png",
        "selectedIconPath": "images/profile-active.png"
      }
    ]
  }
}
```

---

## 📊 数据计算

### 投票权计算

```javascript
// 每 1㎡计 1 票
voteRights = Math.floor(propertyInfo.area)

// 投票权比例（假设小区总面积 10000㎡）
votePercent = (voteRights / 10000 * 100).toFixed(2)
```

### 认证状态映射

```javascript
const statusMap = {
  'approved': { text: '已认证', color: '#07c160', icon: '✅' },
  'pending': { text: '审核中', color: '#ff9500', icon: '⏳' },
  'rejected': { text: '认证失败', color: '#ff4444', icon: '❌' },
  'none': { text: '未认证', color: '#ff4444', icon: '⚠️' }
}
```

---

## ⚠️ 注意事项

### 1. 登录状态检查
- 页面 onLoad 时检查 Token
- 无 Token 自动跳转登录
- Token 失效自动清除

### 2. 数据刷新
- onShow 时刷新认证状态
- 确保状态实时更新

### 3. 隐私保护
- 不显示完整 OpenID
- 手机号脱敏显示
- 房产信息仅本人可见

### 4. 用户体验
- 加载状态提示
- 空状态引导
- 错误友好提示
- 按压反馈效果

---

## 🔄 后续优化

### 短期（本周）
- [ ] 实现投票列表页面
- [ ] 实现会议列表页面
- [ ] 实现通知列表页面
- [ ] 添加消息推送

### 中期（下周）
- [ ] 房产信息接口
- [ ] 投票权统计接口
- [ ] 用户数据看板
- [ ] 分享功能

### 长期
- [ ] 多房产支持
- [ ] 家庭成员管理
- [ ] 委托投票管理
- [ ] 个人中心个性化

---

## 📚 相关文档

- [登录接口实现](./LOGIN_IMPLEMENTATION.md)
- [认证页面实现](./CERTIFY_IMPLEMENTATION.md)
- [Week 1-2 总结](./WEEK1_2_SUMMARY.md)
- [开发计划](./DEVELOPMENT_PLAN.md)

---

**🎉 用户中心页面已完成！用户可以查看个人信息和认证状态了！**
