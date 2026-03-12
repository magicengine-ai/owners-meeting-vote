# 认证页面实现说明

**完成时间：** 2026-03-12 22:45  
**状态：** ✅ 已完成

---

## 📋 实现内容

### 1️⃣ 前端认证页面

#### 页面路径
`/pages/auth/verify/verify`

#### 核心功能

✅ **三步认证流程**
1. **上传房产证** - 拍照或从相册选择
2. **OCR 识别** - 自动识别房产证信息
3. **确认提交** - 确认信息后提交审核

✅ **认证状态展示**
- ✅ 已认证 - 显示成功状态
- ⏳ 审核中 - 显示等待状态
- ❌ 认证失败 - 显示失败原因，支持重新认证

✅ **UI 特性**
- 渐变顶部设计
- 步骤指示器
- 图片预览
- 识别结果卡片
- 加载动画
- 状态卡片

#### 文件结构

```
frontend/pages/auth/verify/
├── verify.js       # 页面逻辑
├── verify.wxml     # 页面结构
├── verify.wxss     # 页面样式
└── verify.json     # 页面配置
```

---

### 2️⃣ 后端 OCR 接口

#### 已实现接口

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| OCR 识别 | POST | `/api/auth/property/ocr` | 识别房产证图片 |
| 提交认证 | POST | `/api/auth/property/verify` | 提交认证信息 |
| 认证状态 | GET | `/api/auth/verify/status` | 查询认证状态 |

#### 核心功能

✅ **百度 AI OCR 集成**
- 调用百度房产证识别 API
- 支持高精度识别
- 自动提取关键信息

✅ **信息提取**
- 产权人姓名
- 房产证号
- 房屋地址
- 建筑面积

✅ **开发环境支持**
- 未安装 SDK 时返回模拟数据
- 便于开发和测试

#### 正则提取函数

```python
- extract_owner_name()    # 提取产权人
- extract_cert_number()   # 提取证号
- extract_address()       # 提取地址
- extract_area()          # 提取面积
```

---

## 🚀 使用流程

### 用户认证流程

```
1. 用户登录小程序
   ↓
2. 进入"我的"页面
   ↓
3. 点击"身份认证"
   ↓
4. 拍摄/上传房产证照片
   ↓
5. 系统自动 OCR 识别
   ↓
6. 用户确认信息
   ↓
7. 提交审核
   ↓
8. 等待管理员审核
   ↓
9. 审核通过，可以投票
```

---

## 📝 测试指南

### 1. 测试 OCR 识别

```bash
# 准备一张房产证图片，转换为 Base64

# 调用 OCR 接口
curl -X POST http://localhost:8000/api/auth/property/ocr \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "YOUR_BASE64_IMAGE",
    "cert_type": "property"
  }'
```

**开发环境：** 无需真实图片，直接返回模拟数据

### 2. 测试认证提交

```bash
# 先登录获取 token
TOKEN="your_access_token"

# 提交认证
curl -X POST http://localhost:8000/api/auth/property/verify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "owner_name": "张三",
    "cert_number": "京 (2024) 朝阳区不动产权第 1234567 号",
    "address": "北京市朝阳区 XX 路 XX 号院",
    "area": 89.5
  }'
```

### 3. 查询认证状态

```bash
curl http://localhost:8000/api/auth/verify/status \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔧 配置说明

### 百度 AI OCR 配置

在 `backend/.env` 文件中配置：

```ini
# OCR 配置（百度 AI）
OCR_APP_ID=your_baidu_app_id
OCR_API_KEY=your_baidu_api_key
OCR_SECRET_KEY=your_baidu_secret_key
```

**获取方式：**
1. 访问 https://ai.baidu.com/
2. 创建应用
3. 选择"文字识别"服务
4. 获取 AppID、API Key、Secret Key

### 安装百度 AI SDK

```bash
cd backend
pip install baidu-aip
```

---

## 📊 识别效果优化

### 拍照建议

✅ **推荐：**
- 光线充足
- 正对房产证
- 保持清晰
- 完整拍摄

❌ **避免：**
- 反光
- 模糊
- 角度倾斜
- 部分遮挡

### 识别准确率

- **理想情况：** 95%+
- **一般情况：** 85%+
- **需要人工审核：** <85%

---

## 🎨 UI 设计特点

### 1. 步骤指示器
```
[1] ── [2] ── [3]
上传   OCR   提交
```
- 当前步骤高亮
- 已完成步骤绿色
- 未完成步骤灰色

### 2. 状态卡片
- **已认证：** 绿色 ✅
- **审核中：** 黄色 ⏳（带脉冲动画）
- **认证失败：** 红色 ❌

### 3. 信息卡片
- 浅灰背景
- 标签 + 内容布局
- 自动换行
- 清晰易读

---

## ⚠️ 注意事项

### 1. 隐私保护
- 图片仅用于 OCR 识别
- 不存储原始图片
- 仅保存识别结果
- 严格保密

### 2. 开发环境
- 无需配置百度 AI
- 自动返回模拟数据
- 便于功能测试

### 3. 生产环境
- 必须配置百度 AI
- 启用 HTTPS
- 图片压缩上传
- 添加水印

### 4. 错误处理
- 网络错误：友好提示
- 识别失败：支持重试
- 信息不符：人工审核

---

## 🔄 后续优化

### 短期（本周）
- [ ] 添加图片裁剪功能
- [ ] 优化识别准确率
- [ ] 添加人工审核后台
- [ ] 审核结果通知

### 中期（下周）
- [ ] 支持多房产证（共有产权）
- [ ] 对接政府系统验证
- [ ] 添加人脸识别
- [ ] 认证记录查询

### 长期
- [ ] 支持更多证件类型
- [ ] 批量认证
- [ ] 认证数据统计
- [ ] 自动审核（AI）

---

## 📚 相关文档

- [登录接口实现](./LOGIN_IMPLEMENTATION.md)
- [测试指南](./TEST_LOGIN.md)
- [API 文档](./API.md)
- [开发计划](./DEVELOPMENT_PLAN.md)

---

**🎉 认证页面已完成！用户可以上传房产证进行身份认证了！**
