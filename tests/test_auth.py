"""
认证模块测试用例
测试登录、短信验证码、用户信息等功能
"""
import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time


class TestWechatLogin:
    """微信登录测试"""
    
    def test_wechat_login_success(self, client):
        """测试微信登录成功"""
        response = client.post(
            "/api/auth/wechat/login",
            json={"code": "test_code_123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "openid" in data
        assert "nickname" in data
    
    def test_wechat_login_invalid_code(self, client):
        """测试微信登录 - 无效 code"""
        response = client.post(
            "/api/auth/wechat/login",
            json={"code": ""}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    def test_wechat_login_missing_code(self, client):
        """测试微信登录 - 缺少 code 参数"""
        response = client.post(
            "/api/auth/wechat/login",
            json={}
        )
        assert response.status_code == 422


class TestPhoneSMS:
    """短信验证码测试"""
    
    def test_send_sms_success(self, client):
        """测试发送短信验证码成功"""
        response = client.post(
            "/api/auth/phone/sms",
            json={"phone": "13800138000"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "sms_token" in data
        assert "expire_seconds" in data
        assert data["expire_seconds"] == 300
    
    def test_send_sms_invalid_phone(self, client):
        """测试发送短信 - 无效手机号"""
        response = client.post(
            "/api/auth/phone/sms",
            json={"phone": "123456"}
        )
        assert response.status_code == 422
    
    def test_send_sms_missing_phone(self, client):
        """测试发送短信 - 缺少手机号"""
        response = client.post(
            "/api/auth/phone/sms",
            json={}
        )
        assert response.status_code == 422
    
    @freeze_time("2026-03-18 10:00:00")
    def test_send_sms_rate_limit(self, client):
        """测试短信发送频率限制"""
        # 第一次发送
        response1 = client.post(
            "/api/auth/phone/sms",
            json={"phone": "13800138000"}
        )
        assert response1.status_code == 200
        
        # 60 秒内再次发送应该被限制
        response2 = client.post(
            "/api/auth/phone/sms",
            json={"phone": "13800138000"}
        )
        assert response2.status_code == 429
        assert "rate_limit" in response2.json()["detail"]


class TestPhoneLogin:
    """手机号登录测试"""
    
    def test_phone_login_success(self, client, db_session):
        """测试手机号登录成功"""
        # 1. 发送验证码
        sms_response = client.post(
            "/api/auth/phone/sms",
            json={"phone": "13800138000"}
        )
        sms_token = sms_response.json()["sms_token"]
        
        # 2. 登录（开发环境验证码固定为 123456）
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
        assert "phone" in data
        assert data["phone"] == "13800138000"
    
    def test_phone_login_wrong_code(self, client, db_session):
        """测试手机号登录 - 验证码错误"""
        sms_response = client.post(
            "/api/auth/phone/sms",
            json={"phone": "13800138000"}
        )
        sms_token = sms_response.json()["sms_token"]
        
        response = client.post(
            "/api/auth/phone/login",
            json={
                "phone": "13800138000",
                "sms_code": "999999",  # 错误验证码
                "sms_token": sms_token
            }
        )
        assert response.status_code == 401
        assert "验证码错误" in response.json()["detail"]
    
    def test_phone_login_expired_code(self, client, db_session):
        """测试手机号登录 - 验证码过期"""
        sms_response = client.post(
            "/api/auth/phone/sms",
            json={"phone": "13800138000"}
        )
        sms_token = sms_response.json()["sms_token"]
        
        # 模拟 6 分钟后（验证码已过期）
        with freeze_time("2026-03-18 10:06:00"):
            response = client.post(
                "/api/auth/phone/login",
                json={
                    "phone": "13800138000",
                    "sms_code": "123456",
                    "sms_token": sms_token
                }
            )
            assert response.status_code == 401
            assert "验证码已过期" in response.json()["detail"]


class TestUserInfo:
    """用户信息测试"""
    
    def test_get_user_info_success(self, client, test_user):
        """测试获取用户信息成功"""
        # 先登录获取 token
        login_response = client.post(
            "/api/auth/wechat/login",
            json={"code": "test_code"}
        )
        token = login_response.json()["access_token"]
        
        # 获取用户信息
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "openid" in data
        assert "nickname" in data
        assert "is_verified" in data
    
    def test_get_user_info_no_token(self, client):
        """测试获取用户信息 - 未授权"""
        response = client.get("/api/auth/me")
        assert response.status_code == 401
    
    def test_get_user_info_invalid_token(self, client):
        """测试获取用户信息 - 无效 Token"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
    
    def test_update_user_info(self, client, test_user):
        """测试更新用户信息"""
        # 登录
        login_response = client.post(
            "/api/auth/wechat/login",
            json={"code": "test_code"}
        )
        token = login_response.json()["access_token"]
        
        # 更新用户信息
        response = client.put(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"nickname": "新昵称"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nickname"] == "新昵称"


class TestTokenRefresh:
    """Token 刷新测试"""
    
    def test_refresh_token_success(self, client):
        """测试刷新 Token 成功"""
        # 登录获取 token
        login_response = client.post(
            "/api/auth/wechat/login",
            json={"code": "test_code"}
        )
        access_token = login_response.json()["access_token"]
        refresh_token = login_response.json().get("refresh_token")
        
        if refresh_token:
            # 刷新 token
            response = client.post(
                "/api/auth/refresh",
                json={"refresh_token": refresh_token}
            )
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
    
    def test_refresh_token_expired(self, client):
        """测试刷新 Token - 已过期"""
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": "expired_token"}
        )
        assert response.status_code == 401


class TestLogout:
    """登出测试"""
    
    def test_logout_success(self, client):
        """测试登出成功"""
        # 登录
        login_response = client.post(
            "/api/auth/wechat/login",
            json={"code": "test_code"}
        )
        token = login_response.json()["access_token"]
        
        # 登出
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        # 验证 token 已失效
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401
