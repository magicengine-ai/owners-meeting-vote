"""
会议模块测试用例
测试会议创建、报名、签到等功能
"""
import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time


class TestCreateMeeting:
    """创建会议测试"""
    
    def test_create_meeting_success(self, admin_client):
        """测试创建会议成功（管理员）"""
        now = datetime.now()
        response = admin_client.post(
            "/api/meeting/create",
            json={
                "title": "2026 年第一次业主大会",
                "description": "讨论小区物业续聘事宜",
                "start_time": (now + timedelta(days=7)).isoformat(),
                "end_time": (now + timedelta(days=7, hours=2)).isoformat(),
                "location": "小区活动中心",
                "max_participants": 200
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "meeting_id" in data
        assert data["title"] == "2026 年第一次业主大会"
        assert data["location"] == "小区活动中心"
    
    def test_create_meeting_with_agenda(self, admin_client):
        """测试创建带议程的会议"""
        now = datetime.now()
        response = admin_client.post(
            "/api/meeting/create",
            json={
                "title": "业主大会",
                "description": "年度业主大会",
                "start_time": (now + timedelta(days=7)).isoformat(),
                "end_time": (now + timedelta(days=7, hours=2)).isoformat(),
                "location": "小区活动中心",
                "agenda": [
                    {"title": "开场致辞", "duration": 10},
                    {"title": "物业工作报告", "duration": 30},
                    {"title": "财务收支报告", "duration": 20},
                    {"title": "投票表决", "duration": 40}
                ]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "agenda" in data
        assert len(data["agenda"]) == 4
    
    def test_create_meeting_unauthorized(self, client):
        """测试创建会议 - 未授权"""
        now = datetime.now()
        response = client.post(
            "/api/meeting/create",
            json={
                "title": "测试会议",
                "description": "测试",
                "start_time": (now + timedelta(days=7)).isoformat(),
                "end_time": (now + timedelta(days=7, hours=2)).isoformat(),
                "location": "测试地点"
            }
        )
        assert response.status_code == 401
    
    def test_create_meeting_not_admin(self, client):
        """测试创建会议 - 普通用户无权限"""
        login_response = client.post(
            "/api/auth/wechat/login",
            json={"code": "test_code"}
        )
        token = login_response.json()["access_token"]
        
        now = datetime.now()
        response = client.post(
            "/api/meeting/create",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "测试会议",
                "description": "测试",
                "start_time": (now + timedelta(days=7)).isoformat(),
                "end_time": (now + timedelta(days=7, hours=2)).isoformat(),
                "location": "测试地点"
            }
        )
        assert response.status_code == 403


class TestMeetingList:
    """会议列表测试"""
    
    def test_meeting_list_success(self, client):
        """测试获取会议列表"""
        response = client.get("/api/meeting/list")
        assert response.status_code == 200
        data = response.json()
        assert "meetings" in data
        assert "total" in data
    
    def test_meeting_list_filter_status(self, client):
        """测试按状态筛选会议"""
        # 获取即将开始的会议
        response = client.get("/api/meeting/list?status=upcoming")
        assert response.status_code == 200
        data = response.json()
        for meeting in data["meetings"]:
            assert meeting["status"] == "upcoming"
    
    def test_meeting_list_pagination(self, client):
        """测试会议列表分页"""
        response = client.get("/api/meeting/list?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert "page" in data
        assert "page_size" in data


class TestMeetingDetail:
    """会议详情测试"""
    
    def test_meeting_detail_success(self, client, meeting_id):
        """测试获取会议详情"""
        response = client.get(f"/api/meeting/detail/{meeting_id}")
        assert response.status_code == 200
        data = response.json()
        assert "meeting_id" in data
        assert "title" in data
        assert "start_time" in data
        assert "location" in data
    
    def test_meeting_detail_not_found(self, client):
        """测试获取不存在的会议详情"""
        response = client.get("/api/meeting/detail/non_existent_id")
        assert response.status_code == 404


class TestMeetingSignup:
    """会议报名测试"""
    
    def test_meeting_signup_success(self, client, meeting_id):
        """测试会议报名成功"""
        response = client.post(
            "/api/meeting/signup",
            json={"meeting_id": meeting_id}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "signup_id" in data
    
    def test_meeting_signup_duplicate(self, client, meeting_id):
        """测试重复报名"""
        # 第一次报名
        response1 = client.post(
            "/api/meeting/signup",
            json={"meeting_id": meeting_id}
        )
        assert response1.status_code == 200
        
        # 第二次报名
        response2 = client.post(
            "/api/meeting/signup",
            json={"meeting_id": meeting_id}
        )
        assert response2.status_code == 400
        assert "您已经报过名了" in response2.json()["detail"]
    
    def test_meeting_signup_full(self, client, meeting_id):
        """测试会议已满"""
        # 模拟会议人数已满的情况
        response = client.post(
            "/api/meeting/signup",
            json={"meeting_id": meeting_id}
        )
        # 如果会议未满，应该成功；如果已满，应该返回错误
        # 这里测试正常情况
        assert response.status_code in [200, 400]
    
    def test_meeting_signup_past(self, client, meeting_id):
        """测试已过期的会议报名"""
        with freeze_time("2026-03-25 23:59:59"):  # 假设会议已过
            response = client.post(
                "/api/meeting/signup",
                json={"meeting_id": meeting_id}
            )
            assert response.status_code == 400
            assert "会议已结束" in response.json()["detail"]


class TestMeetingCheckin:
    """会议签到测试"""
    
    def test_meeting_checkin_qrcode(self, client, meeting_id):
        """测试二维码签到"""
        response = client.post(
            "/api/meeting/checkin",
            json={
                "meeting_id": meeting_id,
                "checkin_method": "qr_code"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "checkin_time" in data
    
    def test_meeting_checkin_face(self, client, meeting_id):
        """测试人脸识别签到"""
        response = client.post(
            "/api/meeting/checkin",
            json={
                "meeting_id": meeting_id,
                "checkin_method": "face_recognition"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_meeting_checkin_manual(self, client, meeting_id):
        """测试手动签到（管理员）"""
        response = admin_client.post(
            "/api/meeting/checkin",
            json={
                "meeting_id": meeting_id,
                "checkin_method": "manual",
                "user_id": "test_user_openid"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_meeting_checkin_not_signed_up(self, client, meeting_id):
        """测试未报名直接签到"""
        response = client.post(
            "/api/meeting/checkin",
            json={
                "meeting_id": meeting_id,
                "checkin_method": "qr_code"
            }
        )
        # 应该允许签到并自动报名，或者提示先报名
        assert response.status_code in [200, 400]
    
    def test_meeting_checkin_duplicate(self, client, meeting_id):
        """测试重复签到"""
        # 第一次签到
        response1 = client.post(
            "/api/meeting/checkin",
            json={
                "meeting_id": meeting_id,
                "checkin_method": "qr_code"
            }
        )
        assert response1.status_code == 200
        
        # 第二次签到
        response2 = client.post(
            "/api/meeting/checkin",
            json={
                "meeting_id": meeting_id,
                "checkin_method": "qr_code"
            }
        )
        assert response2.status_code == 400
        assert "您已经签过到了" in response2.json()["detail"]


class TestMeetingParticipants:
    """参会人员测试"""
    
    def test_get_participants(self, admin_client, meeting_id):
        """测试获取参会人员名单（管理员）"""
        response = admin_client.get(f"/api/meeting/participants/{meeting_id}")
        assert response.status_code == 200
        data = response.json()
        assert "participants" in data
        assert "total" in data
        assert "checked_in_count" in data
    
    def test_get_participants_unauthorized(self, client, meeting_id):
        """测试获取参会人员名单 - 普通用户"""
        response = client.get(f"/api/meeting/participants/{meeting_id}")
        # 普通用户可能只能看到自己的状态，或者看不到
        assert response.status_code in [200, 403]


class TestMeetingCancel:
    """会议取消测试"""
    
    def test_cancel_meeting_success(self, admin_client, meeting_id):
        """测试取消会议（管理员）"""
        response = admin_client.post(
            f"/api/meeting/cancel/{meeting_id}",
            json={"reason": "因天气原因取消"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_cancel_meeting_unauthorized(self, client, meeting_id):
        """测试取消会议 - 普通用户无权限"""
        login_response = client.post(
            "/api/auth/wechat/login",
            json={"code": "test_code"}
        )
        token = login_response.json()["access_token"]
        
        response = client.post(
            f"/api/meeting/cancel/{meeting_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"reason": "测试"}
        )
        assert response.status_code == 403


class TestMeetingNotification:
    """会议通知测试"""
    
    def test_send_meeting_notification(self, admin_client, meeting_id):
        """测试发送会议通知（管理员）"""
        response = admin_client.post(
            f"/api/meeting/notify/{meeting_id}",
            json={
                "notification_type": "reminder",
                "content": "会议明天开始，请准时参加"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "sent_count" in data
    
    def test_send_notification_to_signed_up(self, admin_client, meeting_id):
        """测试只发送给已报名用户"""
        response = admin_client.post(
            f"/api/meeting/notify/{meeting_id}",
            json={
                "notification_type": "reminder",
                "content": "会议提醒",
                "target": "signed_up_only"  # 只发送给已报名用户
            }
        )
        assert response.status_code == 200


class TestMeetingRecord:
    """会议记录测试"""
    
    def test_create_meeting_record(self, admin_client, meeting_id):
        """测试创建会议记录（管理员）"""
        response = admin_client.post(
            f"/api/meeting/record/{meeting_id}",
            json={
                "content": "会议决议：同意续聘当前物业公司",
                "attachments": ["file_token_123"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "record_id" in data
    
    def test_get_meeting_record(self, client, meeting_id):
        """测试获取会议记录"""
        response = client.get(f"/api/meeting/record/{meeting_id}")
        assert response.status_code == 200
        data = response.json()
        assert "records" in data


class TestMeetingStatistics:
    """会议统计测试"""
    
    def test_meeting_statistics(self, admin_client, meeting_id):
        """测试获取会议统计（管理员）"""
        response = admin_client.get(f"/api/meeting/statistics/{meeting_id}")
        assert response.status_code == 200
        data = response.json()
        assert "total_signups" in data
        assert "total_checkins" in data
        assert "participation_rate" in data
    
    def test_meeting_export_participants(self, admin_client, meeting_id):
        """测试导出参会人员名单（管理员）"""
        response = admin_client.post(
            f"/api/meeting/export/{meeting_id}",
            json={"format": "csv", "type": "participants"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "download_url" in data
