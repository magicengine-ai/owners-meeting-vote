# 业主大会投票小程序 - API 文档

**版本：** v1.0  
**更新日期：** 2026-03-11

---

## 📋 目录

1. [认证模块](#认证模块)
2. [投票模块](#投票模块)
3. [会议模块](#会议模块)
4. [区块链存证](#区块链存证)
5. [消息推送](#消息推送)

---

## 🔐 认证模块

### 1. 微信登录

**接口：** `POST /api/auth/wechat/login`

**请求：**
```json
{
  "code": "wx_code_from_miniprogram"
}
```

**响应：**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "openid": "oXXXX-XXXXXXXXXXXXXXXX",
  "is_verified": false
}
```

---

### 2. 房产证 OCR 识别

**接口：** `POST /api/auth/property/ocr`

**请求：**
```json
{
  "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "cert_type": "property"
}
```

**响应：**
```json
{
  "owner_name": "张三",
  "cert_number": "京 (2024) 朝阳区不动产权第 1234567 号",
  "address": "北京市朝阳区 XX 路 XX 号院 X 号楼 X 单元 XXX 室",
  "area": 89.5,
  "confidence": 0.95
}
```

---

### 3. 房产证验证

**接口：** `POST /api/auth/property/verify`

**请求：**
```json
{
  "owner_name": "张三",
  "cert_number": "京 (2024) 朝阳区不动产权第 1234567 号",
  "address": "北京市朝阳区 XX 路 XX 号院 X 号楼 X 单元 XXX 室"
}
```

**响应：**
```json
{
  "status": "approved",
  "message": "验证通过"
}
```

---

### 4. 人脸识别

**接口：** `POST /api/auth/face/recognize`

**请求：**
```json
{
  "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "openid": "oXXXX-XXXXXXXXXXXXXXXX"
}
```

**响应：**
```json
{
  "status": "approved",
  "confidence": 0.98
}
```

---

### 5. 查询认证状态

**接口：** `GET /api/auth/verify/status?openid=xxx`

**响应：**
```json
{
  "status": "pending",
  "message": "认证审核中",
  "verified_at": null
}
```

---

### 6. 绑定楼栋信息

**接口：** `POST /api/auth/bind/building`

**请求：**
```json
{
  "openid": "oXXXX-XXXXXXXXXXXXXXXX",
  "building_id": 1,
  "unit_id": 2,
  "room_id": 301
}
```

**响应：**
```json
{
  "status": "success",
  "message": "绑定成功"
}
```

---

## 🗳️ 投票模块

### 1. 创建投票

**接口：** `POST /api/vote/create`

**请求头：**
```
Authorization: Bearer {access_token}
```

**请求：**
```json
{
  "title": "关于聘请新物业公司的投票",
  "description": "根据业主大会决议，现对聘请新物业公司进行投票",
  "start_time": "2026-03-10T00:00:00+08:00",
  "end_time": "2026-03-20T23:59:59+08:00",
  "options": ["赞成", "反对", "弃权"],
  "vote_type": "single",
  "min_votes": 1,
  "max_votes": 1,
  "pass_threshold": 0.5
}
```

**响应：**
```json
{
  "vote_id": "vote_001",
  "title": "关于聘请新物业公司的投票",
  "status": "active"
}
```

---

### 2. 投票列表

**接口：** `GET /api/vote/list?status=active&page=1&page_size=10`

**响应：**
```json
{
  "total": 5,
  "page": 1,
  "page_size": 10,
  "votes": [
    {
      "vote_id": "vote_001",
      "title": "关于聘请新物业公司的投票",
      "start_time": "2026-03-10T00:00:00+08:00",
      "end_time": "2026-03-20T23:59:59+08:00",
      "status": "active",
      "total_votes": 156
    }
  ]
}
```

---

### 3. 投票详情

**接口：** `GET /api/vote/detail/{vote_id}`

**响应：**
```json
{
  "vote_id": "vote_001",
  "title": "关于聘请新物业公司的投票",
  "description": "根据业主大会决议...",
  "options": ["赞成", "反对", "弃权"],
  "start_time": "2026-03-10T00:00:00+08:00",
  "end_time": "2026-03-20T23:59:59+08:00",
  "status": "active",
  "total_votes": 156,
  "total_households": 500
}
```

---

### 4. 提交投票

**接口：** `POST /api/vote/submit`

**请求：**
```json
{
  "vote_id": "vote_001",
  "options": ["赞成"],
  "proxy_openid": null
}
```

**响应：**
```json
{
  "success": true,
  "vote_record_id": "record_001",
  "timestamp": "2026-03-15T14:30:00+08:00"
}
```

---

### 5. 投票结果

**接口：** `GET /api/vote/result/{vote_id}`

**响应：**
```json
{
  "vote_id": "vote_001",
  "title": "关于聘请新物业公司的投票",
  "total_votes": 156,
  "results": [
    {
      "option": "赞成",
      "count": 120,
      "percentage": 0.769
    },
    {
      "option": "反对",
      "count": 30,
      "percentage": 0.192
    },
    {
      "option": "弃权",
      "count": 6,
      "percentage": 0.038
    }
  ],
  "status": "active",
  "passed": true
}
```

---

### 6. 委托投票

**接口：** `POST /api/vote/proxy/assign`

**请求：**
```json
{
  "proxy_openid": "oXXXX-XXXXXXXXXXXXXXXX",
  "vote_id": "vote_001"
}
```

**响应：**
```json
{
  "success": true,
  "message": "委托成功"
}
```

---

## 📅 会议模块

### 1. 创建会议

**接口：** `POST /api/meeting/create`

**请求：**
```json
{
  "title": "2026 年第一次业主大会",
  "description": "讨论小区物业管理事宜",
  "start_time": "2026-03-25T14:00:00+08:00",
  "end_time": "2026-03-25T17:00:00+08:00",
  "location": "小区活动中心",
  "agenda": [
    {"title": "签到", "time": "14:00-14:30"},
    {"title": "物业报告", "time": "14:30-15:30"},
    {"title": "业主讨论", "time": "15:30-16:30"},
    {"title": "投票表决", "time": "16:30-17:00"}
  ]
}
```

**响应：**
```json
{
  "meeting_id": "meeting_001",
  "title": "2026 年第一次业主大会",
  "status": "upcoming"
}
```

---

### 2. 会议列表

**接口：** `GET /api/meeting/list?status=upcoming`

**响应：**
```json
{
  "total": 3,
  "meetings": [
    {
      "meeting_id": "meeting_001",
      "title": "2026 年第一次业主大会",
      "start_time": "2026-03-25T14:00:00+08:00",
      "location": "小区活动中心",
      "status": "upcoming"
    }
  ]
}
```

---

### 3. 会议签到

**接口：** `POST /api/meeting/checkin`

**请求：**
```json
{
  "meeting_id": "meeting_001",
  "check_in_method": "qr_code"
}
```

**响应：**
```json
{
  "success": true,
  "check_in_time": "2026-03-25T14:15:00+08:00"
}
```

---

## 🔗 区块链存证

### 1. 投票存证

**接口：** `POST /api/chain/vote/proof`

**请求：**
```json
{
  "vote_record_id": "record_001"
}
```

**响应：**
```json
{
  "tx_hash": "0x1234567890abcdef...",
  "block_number": 12345678,
  "timestamp": "2026-03-15T14:30:05+08:00"
}
```

---

### 2. 存证查询

**接口：** `GET /api/chain/proof?record_type=vote&record_id=1`

**响应：**
```json
{
  "tx_hash": "0x1234567890abcdef...",
  "block_number": 12345678,
  "timestamp": "2026-03-15T14:30:05+08:00",
  "data_hash": "sha256:abc123..."
}
```

---

## 📱 消息推送

### 1. 发送小程序消息

**接口：** `POST /api/push/miniprogram`

**请求：**
```json
{
  "openid": "oXXXX-XXXXXXXXXXXXXXXX",
  "template_id": "tmpl_vote_start",
  "data": {
    "vote_title": "关于聘请新物业公司的投票",
    "start_time": "2026-03-10 00:00",
    "end_time": "2026-03-20 23:59"
  },
  "page": "pages/vote/detail?id=vote_001"
}
```

**响应：**
```json
{
  "success": true,
  "message_id": "msg_001"
}
```

---

### 2. 发送短信

**接口：** `POST /api/push/sms`

**请求：**
```json
{
  "phone": "13800138000",
  "template": "【业主大会】您有新的投票待参与，请及时处理。"
}
```

**响应：**
```json
{
  "success": true,
  "message_id": "sms_001"
}
```

---

## ❌ 错误码

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未授权/Token 无效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

**文档结束**
