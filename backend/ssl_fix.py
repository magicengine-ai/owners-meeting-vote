# SSL 补丁 - 必须在所有导入之前
import os
import ssl
import warnings

# 禁用 SSL 验证（微信云托管环境需要）
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['SSL_CERT_FILE'] = '/dev/null'
os.environ['REQUESTS_CA_BUNDLE'] = '/dev/null'

# 忽略 SSL 警告
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
warnings.filterwarnings('ignore', message='SSL is disabled')

# 创建不验证 SSL 的上下文
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except:
    pass

print("SSL 补丁已应用：禁用 SSL 验证")
