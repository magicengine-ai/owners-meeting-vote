# 🧪 测试指南

**最后更新：** 2026-03-12  
**版本：** v1.0.0  
**测试覆盖率：** 90%

---

## 📋 测试环境准备

### 1. 本地测试环境

```bash
# 1. 安装测试依赖
cd backend
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov httpx

# 2. 创建测试数据库
cp .env.example .env.test

# 3. 配置测试环境
# .env.test 内容：
DEBUG=true
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vote_db_test
DB_USER=postgres
DB_PASSWORD=postgres
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 2. Docker 测试环境

```bash
# 使用 docker-compose 启动测试环境
docker-compose -f docker/docker-compose.test.yml up -d
```

---

## 🔧 运行测试

### 单元测试

```bash
# 1. 运行所有测试
pytest tests/ -v

# 2. 运行特定模块测试
pytest tests/test_auth.py -v
pytest tests/test_vote.py -v
pytest tests/test_meeting.py -v

# 3. 运行并生成覆盖率报告
pytest tests/ -v --cov=src --cov-report=html

# 4. 查看覆盖率报告
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov\\index.html  # Windows
```

### 集成测试

```bash
# 1. 启动测试服务
docker-compose -f docker/docker-compose.test.yml up -d

# 2. 运行集成测试
pytest tests/integration/ -v

# 3. 停止测试服务
docker-compose -f docker/docker-compose.test.yml down
```

---

## 📝 测试用例

### 1. 认证模块测试

```python
# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_wechat_login():
    """测试微信登录"""
    response = client.post(
        "/api/auth/wechat/login",
        json={"code": "test_code_123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "openid" in data

def test_phone_sms():
    """测试发送短信验证码"""
    response = client.post(
        "/api/auth/phone/sms",
        json={"phone": "13800138000"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "sms_token" in data

def test_phone_login():
    """测试手机号登录"""
    # 1. 发送验证码
    sms_response = client.post(
        "/api/auth/phone/sms",
        json={"phone": "13800138000"}
    )
    sms_token = sms_response.json()["sms_token"]
    
    # 2. 登录（开发环境验证码在日志中）
    response = client.post(
        "/api/auth/phone/login",
        json={
            "phone": "13800138000",
            "sms_code": "123456",
            "sms_token": sms_token
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_get_user_info():
    """测试获取用户信息"""
    # 1. 登录获取 token
    login_response = client.post(
        "/api/auth/wechat/login",
        json={"code": "test_code"}
    )
    token = login_response.json()["access_token"]
    
    # 2. 获取用户信息
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "openid" in data
```

### 2. 投票模块测试

```python
# tests/test_vote.py
import pytest
from datetime import datetime, timedelta

def test_create_vote(admin_client):
    """测试创建投票（管理员）"""
    response = admin_client.post(
        "/api/vote/create",
        json={
            "title": "测试投票",
            "description": "这是一个测试投票",
            "start_time": (datetime.now()).isoformat(),
            "end_time": (datetime.now() + timedelta(days=7)).isoformat(),
            "options": ["赞成", "反对", "弃权"],
            "vote_type": "single"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "vote_id" in data
    assert data["title"] == "测试投票"

def test_vote_list(client):
    """测试投票列表"""
    response = client.get("/api/vote/list")
    assert response.status_code == 200
    data = response.json()
    assert "votes" in data
    assert "total" in data

def test_vote_detail(client, vote_id):
    """测试投票详情"""
    response = client.get(f"/api/vote/detail/{vote_id}")
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "options" in data

def test_submit_vote(client, vote_id):
    """测试提交投票"""
    response = client.post(
        "/api/vote/submit",
        json={
            "vote_id": str(vote_id),
            "options": ["赞成"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "vote_record_id" in data

def test_vote_result(client, vote_id):
    """测试投票结果"""
    response = client.get(f"/api/vote/result/{vote_id}")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total_votes" in data
```

### 3. 会议模块测试

```python
# tests/test_meeting.py
from datetime import datetime, timedelta

def test_create_meeting(admin_client):
    """测试创建会议（管理员）"""
    response = admin_client.post(
        "/api/meeting/create",
        json={
            "title": "测试会议",
            "description": "这是一个测试会议",
            "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
            "location": "会议室 A"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "meeting_id" in data

def test_meeting_list(client):
    """测试会议列表"""
    response = client.get("/api/meeting/list")
    assert response.status_code == 200
    data = response.json()
    assert "meetings" in data

def test_meeting_signup(client, meeting_id):
    """测试会议报名"""
    response = client.post(
        "/api/meeting/signup",
        json={"meeting_id": meeting_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_meeting_checkin(client, meeting_id):
    """测试会议签到"""
    response = client.post(
        "/api/meeting/checkin",
        json={
            "meeting_id": meeting_id,
            "check_in_method": "qr_code"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "check_in_time" in data
```

### 4. 管理后台测试

```python
# tests/test_admin.py
def test_verify_approve(admin_client, user_id):
    """测试审核通过"""
    response = admin_client.post(
        "/api/admin/verify/approve",
        json={"user_id": user_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_verify_reject(admin_client, user_id):
    """测试审核拒绝"""
    response = admin_client.post(
        "/api/admin/verify/reject",
        json={
            "user_id": user_id,
            "reason": "房产证照片不清晰，请重新上传"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_batch_verify(admin_client, user_ids):
    """测试批量审核"""
    response = admin_client.post(
        "/api/admin/verify/batch",
        json={
            "user_ids": user_ids,
            "action": "approve"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "success_count" in data
    assert "failed_count" in data
```

---

## 📊 性能测试

### 1. 并发登录测试

```bash
# 使用 ab (Apache Bench)
ab -n 1000 -c 100 \
  -T application/json \
  -p login.json \
  https://your-domain.com/api/auth/wechat/login

# login.json 内容：
# {"code":"test_code"}
```

### 2. 并发投票测试

```bash
# 使用 locust
pip install locust

# 创建 locustfile.py
cat > locustfile.py << 'EOF'
from locust import HttpUser, task, between

class VoteUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def vote_list(self):
        self.client.get("/api/vote/list")
    
    @task(2)
    def vote_detail(self):
        self.client.get("/api/vote/detail/1")
    
    @task(1)
    def submit_vote(self):
        self.client.post(
            "/api/vote/submit",
            json={"vote_id": "1", "options": ["赞成"]}
        )
EOF

# 启动测试
locust -f locustfile.py --host=https://your-domain.com

# 访问 http://localhost:8089 查看测试报告
```

### 3. 数据库性能测试

```bash
# 1. 查看慢查询
docker-compose exec db psql -U postgres -d vote_db -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# 2. 分析表
docker-compose exec db psql -U postgres -d vote_db -c "ANALYZE;"

# 3. 查看索引使用情况
docker-compose exec db psql -U postgres -d vote_db -c "SELECT * FROM pg_stat_user_indexes;"
```

---

## 🔒 安全测试

### 1. SQL 注入测试

```bash
# 测试登录接口
curl -X POST https://your-domain.com/api/auth/wechat/login \
  -H "Content-Type: application/json" \
  -d '{"code":"test\' OR \'1\'=\'1"}'

# 预期：应该返回错误，而不是登录成功
```

### 2. XSS 测试

```bash
# 测试投票创建
curl -X POST https://your-domain.com/api/vote/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"title":"<script>alert(1)</script>","description":"test","start_time":"2026-03-13T00:00:00","end_time":"2026-03-20T00:00:00","options":["A","B"]}'

# 预期：应该过滤或转义 HTML 标签
```

### 3. 权限测试

```bash
# 1. 未授权访问管理接口
curl https://your-domain.com/api/admin/verify/pending
# 预期：401 Unauthorized

# 2. 普通用户访问管理接口
curl -H "Authorization: Bearer USER_TOKEN" \
  https://your-domain.com/api/admin/verify/pending
# 预期：403 Forbidden

# 3. 管理员访问
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  https://your-domain.com/api/admin/verify/pending
# 预期：200 OK
```

---

## 📈 测试报告

### 生成测试报告

```bash
# 1. 运行测试并生成报告
pytest tests/ -v --cov=src --cov-report=html --cov-report=xml

# 2. 生成 JUnit 格式报告
pytest tests/ -v --junitxml=test-results.xml

# 3. 查看覆盖率
pytest tests/ -v --cov=src --cov-report=term-missing
```

### 测试覆盖率要求

| 模块 | 最低覆盖率 | 目标覆盖率 |
|------|-----------|-----------|
| 认证模块 | 90% | 95% |
| 投票模块 | 85% | 92% |
| 会议模块 | 85% | 90% |
| 管理后台 | 80% | 88% |
| 消息推送 | 80% | 85% |
| **总计** | **85%** | **90%** |

---

## 🐛 Bug 报告模板

```markdown
## Bug 描述
简要描述 Bug 现象

## 复现步骤
1. 步骤 1
2. 步骤 2
3. 步骤 3

## 预期结果
应该发生什么

## 实际结果
实际发生了什么

## 环境信息
- 操作系统：Ubuntu 20.04
- Python 版本：3.11
- 浏览器：Chrome 120

## 日志
```
粘贴相关日志
```

## 截图
（如有）
```

---

## 📞 技术支持

- **GitHub Issues:** https://github.com/magicengine-ai/owners-meeting-vote/issues
- **测试问题:** 提交 Issue 时标注 [Test] 标签

---

**🎉 测试完成！确保质量！**
