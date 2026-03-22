# 后端 SSL 问题修复指南

## 问题
微信云托管环境调用微信 API 时报 SSL 证书验证错误：
```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate
```

## 解决方案

### 方案 1：在代码中禁用 SSL 验证（推荐）

#### 步骤 1：创建 SSL 补丁文件

已创建 `backend/ssl_patch.py`，内容如下：

```python
import urllib3
import requests

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 重写 request 方法，对微信 API 禁用 SSL 验证
original_request = requests.Session.request

def patched_request(self, method, url, *args, **kwargs):
    if 'api.weixin.qq.com' in url:
        kwargs['verify'] = False
    return original_request(self, method, url, *args, **kwargs)

requests.Session.request = patched_request
```

#### 步骤 2：在主应用中引入补丁

在 `backend/main.py` 的**最开头**添加：

```python
# 在导入其他模块之前
from ssl_patch import *  # 应用 SSL 补丁

from fastapi import FastAPI
# ... 其他导入
```

或者在 `backend/src/auth/wechat.py` 的开头添加：

```python
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
# ... 其他代码
```

#### 步骤 3：修改微信 API 调用

在调用微信 API 的地方，添加 `verify=False`：

```python
# 修改前
response = requests.get(url, params=params)

# 修改后
response = requests.get(url, params=params, verify=False)
```

---

### 方案 2：使用环境变量（临时方案）

在微信云托管控制台的环境变量中添加：

```
PYTHONHTTPSVERIFY=0
```

这会全局禁用 Python 的 SSL 验证（不推荐生产环境）。

---

## 部署步骤

1. **提交代码**
   ```bash
   git add backend/ssl_patch.py
   git add backend/main.py  # 如果修改了
   git commit -m "fix: 禁用微信 API 的 SSL 验证"
   git push origin main
   ```

2. **重新部署**
   - 微信云托管控制台 → 版本管理
   - 部署新版本
   - 等待构建完成

3. **测试**
   - 小程序清除缓存
   - 重新编译
   - 测试微信登录

---

## 验证成功标志

后端日志应该显示：
```
✅ POST /api/auth/wechat/login - 200 OK
✅ 微信登录成功
```

而不是：
```
❌ [SSL: CERTIFICATE_VERIFY_FAILED]
```

---

## 安全说明

⚠️ **仅限开发/测试环境使用**

生产环境应该：
1. 使用正确的 CA 证书
2. 启用 SSL 验证（`verify=True`）
3. 或使用微信官方的 Python SDK

---

**最后更新：** 2026-03-22
