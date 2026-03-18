"""
管理后台测试用例
测试认证审核、用户管理、数据统计等功能
"""
import pytest
from datetime import datetime, timedelta


class TestVerifyPending:
    """待审核列表测试"""
    
    def test_get_verify_pending_success(self, admin_client):
        """测试获取待审核列表（管理员）"""
        response = admin_client.get("/api/admin/verify/pending")
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert isinstance(data["users"], list)
    
    def test_get_verify_pending_pagination(self, admin_client):
        """测试待审核列表分页"""
        response = admin_client.get("/api/admin/verify/pending?page=1&page_size=20")
        assert response.status_code == 200
        data = response.json()
        assert "page" in data
        assert "page_size" in data
        assert len(data["users"]) <= 20
    
    def test_get_verify_pending_unauthorized(self, client):
        """测试获取待审核列表 - 未授权"""
        response = client.get("/api/admin/verify/pending")
        assert response.status_code == 401
    
    def test_get_verify_pending_not_admin(self, client):
        """测试获取待审核列表 - 普通用户无权限"""
        login_response = client.post(
            "/api/auth/wechat/login",
            json={"code": "test_code"}
        )
        token = login_response.json()["access_token"]
        
        response = client.get(
            "/api/admin/verify/pending",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403


class TestVerifyApprove:
    """审核通过测试"""
    
    def test_approve_success(self, admin_client, user_id):
        """测试审核通过"""
        response = admin_client.post(
            "/api/admin/verify/approve",
            json={"user_id": user_id}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "user_id" in data
    
    def test_approve_non_existent_user(self, admin_client):
        """测试审核不存在的用户"""
        response = admin_client.post(
            "/api/admin/verify/approve",
            json={"user_id": "non_existent_id"}
        )
        assert response.status_code == 404
    
    def test_approve_already_verified(self, admin_client, verified_user_id):
        """测试审核已通过的用户"""
        response = admin_client.post(
            "/api/admin/verify/approve",
            json={"user_id": verified_user_id}
        )
        assert response.status_code == 400
        assert "该用户已通过认证" in response.json()["detail"]


class TestVerifyReject:
    """审核拒绝测试"""
    
    def test_reject_success(self, admin_client, user_id):
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
    
    def test_reject_missing_reason(self, admin_client, user_id):
        """测试审核拒绝 - 缺少原因"""
        response = admin_client.post(
            "/api/admin/verify/reject",
            json={"user_id": user_id}
        )
        assert response.status_code == 422
    
    def test_reject_empty_reason(self, admin_client, user_id):
        """测试审核拒绝 - 原因不能为空"""
        response = admin_client.post(
            "/api/admin/verify/reject",
            json={
                "user_id": user_id,
                "reason": ""
            }
        )
        assert response.status_code == 400


class TestBatchVerify:
    """批量审核测试"""
    
    def test_batch_approve_success(self, admin_client, user_ids):
        """测试批量审核通过"""
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
        assert data["success_count"] > 0
    
    def test_batch_reject_success(self, admin_client, user_ids):
        """测试批量审核拒绝"""
        response = admin_client.post(
            "/api/admin/verify/batch",
            json={
                "user_ids": user_ids,
                "action": "reject",
                "reason": "批量审核拒绝"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "success_count" in data
    
    def test_batch_verify_empty_list(self, admin_client):
        """测试批量审核 - 空列表"""
        response = admin_client.post(
            "/api/admin/verify/batch",
            json={
                "user_ids": [],
                "action": "approve"
            }
        )
        assert response.status_code == 400
        assert "用户列表不能为空" in response.json()["detail"]
    
    def test_batch_verify_invalid_action(self, admin_client, user_ids):
        """测试批量审核 - 无效操作"""
        response = admin_client.post(
            "/api/admin/verify/batch",
            json={
                "user_ids": user_ids,
                "action": "invalid_action"
            }
        )
        assert response.status_code == 400


class TestUserManagement:
    """用户管理测试"""
    
    def test_get_user_list(self, admin_client):
        """测试获取用户列表"""
        response = admin_client.get("/api/admin/users")
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
    
    def test_get_user_list_filter_verified(self, admin_client):
        """测试按认证状态筛选用户"""
        response = admin_client.get("/api/admin/users?verified=true")
        assert response.status_code == 200
        data = response.json()
        for user in data["users"]:
            assert user["is_verified"] is True
    
    def test_get_user_detail(self, admin_client, user_id):
        """测试获取用户详情"""
        response = admin_client.get(f"/api/admin/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "openid" in data
        assert "nickname" in data
    
    def test_update_user_role(self, admin_client, user_id):
        """测试更新用户角色"""
        response = admin_client.put(
            f"/api/admin/users/{user_id}/role",
            json={"role": "admin"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "admin"
    
    def test_ban_user(self, admin_client, user_id):
        """测试封禁用户"""
        response = admin_client.post(
            f"/api/admin/users/{user_id}/ban",
            json={"reason": "违规操作", "duration_days": 30}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_unban_user(self, admin_client, user_id):
        """测试解封用户"""
        response = admin_client.post(
            f"/api/admin/users/{user_id}/unban"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestVoteManagement:
    """投票管理测试"""
    
    def test_get_vote_list(self, admin_client):
        """测试获取投票列表（管理员）"""
        response = admin_client.get("/api/admin/votes")
        assert response.status_code == 200
        data = response.json()
        assert "votes" in data
    
    def test_update_vote(self, admin_client, vote_id):
        """测试更新投票"""
        response = admin_client.put(
            f"/api/admin/votes/{vote_id}",
            json={"title": "更新后的投票标题"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "更新后的投票标题"
    
    def test_delete_vote(self, admin_client, vote_id):
        """测试删除投票"""
        response = admin_client.delete(f"/api/admin/votes/{vote_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_end_vote_early(self, admin_client, vote_id):
        """测试提前结束投票"""
        response = admin_client.post(
            f"/api/admin/votes/{vote_id}/end",
            json={"reason": "投票已充分，提前结束"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestMeetingManagement:
    """会议管理测试"""
    
    def test_get_meeting_list(self, admin_client):
        """测试获取会议列表（管理员）"""
        response = admin_client.get("/api/admin/meetings")
        assert response.status_code == 200
        data = response.json()
        assert "meetings" in data
    
    def test_update_meeting(self, admin_client, meeting_id):
        """测试更新会议"""
        response = admin_client.put(
            f"/api/admin/meetings/{meeting_id}",
            json={"title": "更新后的会议标题"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "更新后的会议标题"
    
    def test_delete_meeting(self, admin_client, meeting_id):
        """测试删除会议"""
        response = admin_client.delete(f"/api/admin/meetings/{meeting_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestStatistics:
    """数据统计测试"""
    
    def test_dashboard_statistics(self, admin_client):
        """测试获取仪表盘统计"""
        response = admin_client.get("/api/admin/statistics/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_votes" in data
        assert "total_meetings" in data
        assert "verified_users" in data
    
    def test_user_growth_statistics(self, admin_client):
        """测试获取用户增长统计"""
        response = admin_client.get("/api/admin/statistics/user-growth")
        assert response.status_code == 200
        data = response.json()
        assert "growth_data" in data
        assert isinstance(data["growth_data"], list)
    
    def test_vote_participation_statistics(self, admin_client):
        """测试获取投票参与率统计"""
        response = admin_client.get("/api/admin/statistics/vote-participation")
        assert response.status_code == 200
        data = response.json()
        assert "participation_data" in data
    
    def test_export_statistics(self, admin_client):
        """测试导出统计数据"""
        response = admin_client.post(
            "/api/admin/statistics/export",
            json={
                "type": "all",
                "format": "csv",
                "start_date": "2026-03-01",
                "end_date": "2026-03-31"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "download_url" in data


class TestSystemSettings:
    """系统设置测试"""
    
    def test_get_settings(self, admin_client):
        """测试获取系统设置"""
        response = admin_client.get("/api/admin/settings")
        assert response.status_code == 200
        data = response.json()
        assert "settings" in data
    
    def test_update_settings(self, admin_client):
        """测试更新系统设置"""
        response = admin_client.put(
            "/api/admin/settings",
            json={
                "verify_required": True,
                "vote_anonymous": False,
                "meeting_signup_required": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["verify_required"] is True
    
    def test_get_system_logs(self, admin_client):
        """测试获取系统日志"""
        response = admin_client.get("/api/admin/logs")
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert "total" in data
    
    def test_get_logs_filter_level(self, admin_client):
        """测试按级别筛选日志"""
        response = admin_client.get("/api/admin/logs?level=ERROR")
        assert response.status_code == 200
        data = response.json()
        for log in data["logs"]:
            assert log["level"] == "ERROR"


class TestAdminAuth:
    """管理员认证测试"""
    
    def test_admin_login_success(self, client):
        """测试管理员登录"""
        response = client.post(
            "/api/admin/login",
            json={
                "username": "admin",
                "password": "admin_password"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data.get("is_admin") is True
    
    def test_admin_login_wrong_password(self, client):
        """测试管理员登录 - 密码错误"""
        response = client.post(
            "/api/admin/login",
            json={
                "username": "admin",
                "password": "wrong_password"
            }
        )
        assert response.status_code == 401
    
    def test_admin_login_not_admin(self, client):
        """测试普通用户尝试管理员登录"""
        response = client.post(
            "/api/admin/login",
            json={
                "username": "normal_user",
                "password": "password"
            }
        )
        assert response.status_code == 403
        assert "非管理员用户" in response.json()["detail"]
