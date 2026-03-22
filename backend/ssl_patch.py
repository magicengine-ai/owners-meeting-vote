# SSL 证书修复补丁
# 在后端代码中禁用 SSL 验证（微信云托管环境需要）

import urllib3
import requests

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 保存原始的 request 方法
original_request = requests.Session.request

# 重写 request 方法，默认禁用 SSL 验证
def patched_request(self, method, url, *args, **kwargs):
    # 只对微信 API 禁用 SSL 验证
    if 'api.weixin.qq.com' in url:
        kwargs['verify'] = False
    return original_request(self, method, url, *args, **kwargs)

# 应用补丁
requests.Session.request = patched_request

# 在应用启动时调用
print("SSL 补丁已应用：微信 API 将禁用 SSL 验证")
