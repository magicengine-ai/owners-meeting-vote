"""
消息推送模块测试用例
测试微信模板消息、短信推送等功能
"""
import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time


class TestWechatTemplateMessage:
    """微信模板消息测试"""
    
    def test_send_template_success(self, admin_client):
        """测试发送微信模板消息成功"""
        response = admin_client.post(
            "/api/push/wechat/template",
            json={
                "user_openid": "test_user_openid",
                "template_id": "template_id_123",
                "data": {
                    "title": {"value": "会议通知", "color": "#173177"},
                    "time": {"value": "2026-03-25 14:00", "color": "#173177"},
                    "location": {"value": "小区活动中心", "color": "#173177"}
                },
                "page": "pages/meeting/detail"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message_id" in data
    
    def test_send_template_missing_data(self, admin_client):
        """测试发送模板消息 - 缺少必要数据"""
        response = admin_client.post(
            "/api/push/wechat/template",
            json={
                "user_openid": "test_user_openid",
                "template_id": "template_id_123"
                # 缺少 data 字段
            }
        )
        assert response.status_code == 422
    
    def test_send_template_invalid_user(self, admin_client):
        """测试发送模板消息 - 无效用户"""
        response = admin_client.post(
            "/api/push/wechat/template",
            json={
                "user_openid": "invalid_openid",
                "template_id": "template_id_123",
                "data": {"title": {"value": "测试"}}
            }
        )
        assert response.status_code == 404
        assert "用户不存在" in response.json()["detail"]


class TestSmsPush:
    """短信推送测试"""
    
    def test_send_sms_success(self, admin_client):
        """测试发送短信成功"""
        response = admin_client.post(
            "/api/push/sms/send",
            json={
                "phone": "13800138000",
                "content": "【小区通知】您有一条新消息，请及时查看"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message_id" in data
    
    def test_send_sms_invalid_phone(self, admin_client):
        """测试发送短信 - 无效手机号"""
        response = admin_client.post(
            "/api/push/sms/send",
            json={
                "phone": "123456",
                "content": "测试短信"
            }
        )
        assert response.status_code == 400
        assert "手机号格式错误" in response.json()["detail"]
    
    def test_send_sms_content_too_long(self, admin_client):
        """测试发送短信 - 内容过长"""
        response = admin_client.post(
            "/api/push/sms/send",
            json={
                "phone": "13800138000",
                "content": "测试" * 500  # 超过短信长度限制
            }
        )
        assert response.status_code == 400
        assert "短信内容过长" in response.json()["detail"]


class TestVoteNotification:
    """投票通知测试"""
    
    def test_notify_new_vote(self, admin_client, vote_id):
        """测试新投票通知"""
        response = admin_client.post(
            f"/api/push/vote/notify/{vote_id}",
            json={
                "notification_type": "new_vote",
                "target_users": "all_verified"  # 发送给所有认证用户
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "sent_count" in data
        assert "failed_count" in data
    
    def test_notify_vote_ending(self, admin_client, vote_id):
        """测试投票即将结束通知"""
        response = admin_client.post(
            f"/api/push/vote/notify/{vote_id}",
            json={
                "notification_type": "ending_soon",
                "hours_left": 24  # 剩余 24 小时
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "sent_count" in data
    
    def test_notify_vote_result(self, admin_client, vote_id):
        """测试投票结果通知"""
        response = admin_client.post(
            f"/api/push/vote/notify/{vote_id}",
            json={
                "notification_type": "result",
                "target": "voters_only"  # 只发送给参与投票的用户
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "sent_count" in data
    
    def test_notify_unvoted_users(self, admin_client, vote_id):
        """测试通知未投票用户"""
        response = admin_client.post(
            f"/api/push/vote/remind/{vote_id}",
            json={
                "reminder_type": "unvoted_users",
                "message": "投票即将结束，请尽快参与"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "reminded_count" in data


class TestMeetingNotification:
    """会议通知测试"""
    
    def test_notify_new_meeting(self, admin_client, meeting_id):
        """测试新会议通知"""
        response = admin_client.post(
            f"/api/push/meeting/notify/{meeting_id}",
            json={
                "notification_type": "new_meeting",
                "target": "all_users"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "sent_count" in data
    
    def test_notify_meeting_reminder(self, admin_client, meeting_id):
        """测试会议提醒通知"""
        with freeze_time("2026-03-24 10:00:00"):  # 会议前一天
            response = admin_client.post(
                f"/api/push/meeting/notify/{meeting_id}",
                json={
                    "notification_type": "reminder",
                    "time_before": "1d"  # 提前 1 天
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert "sent_count" in data
    
    def test_notify_meeting_start(self, admin_client, meeting_id):
        """测试会议开始通知"""
        with freeze_time("2026-03-25 13:00:00"):  # 会议开始前 1 小时
            response = admin_client.post(
                f"/api/push/meeting/notify/{meeting_id}",
                json={
                    "notification_type": "starting_soon",
                    "time_before": "1h"
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert "sent_count" in data
    
    def test_notify_meeting_change(self, admin_client, meeting_id):
        """测试会议变更通知"""
        response = admin_client.post(
            f"/api/push/meeting/notify/{meeting_id}",
            json={
                "notification_type": "change",
                "change_reason": "因天气原因，会议地点改为室内",
                "target": "signed_up_users"  # 只通知已报名用户
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "sent_count" in data
    
    def test_notify_meeting_cancel(self, admin_client, meeting_id):
        """测试会议取消通知"""
        response = admin_client.post(
            f"/api/push/meeting/notify/{meeting_id}",
            json={
                "notification_type": "cancelled",
                "cancel_reason": "因不可抗力因素，会议取消",
                "target": "all_signed_up"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "sent_count" in data


class TestScheduledPush:
    """定时推送测试"""
    
    def test_create_scheduled_task(self, admin_client):
        """测试创建定时推送任务"""
        response = admin_client.post(
            "/api/push/schedule/create",
            json={
                "task_type": "vote_notification",
                "target_id": "vote_id_123",
                "scheduled_time": "2026-03-25T10:00:00",
                "notification_type": "reminder",
                "target_users": "all_verified"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["scheduled_time"] == "2026-03-25T10:00:00"
    
    def test_cancel_scheduled_task(self, admin_client):
        """测试取消定时推送任务"""
        response = admin_client.post(
            "/api/push/schedule/cancel",
            json={"task_id": "task_id_123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_scheduled_tasks(self, admin_client):
        """测试获取定时推送任务列表"""
        response = admin_client.get("/api/push/schedule/list")
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data
    
    def test_get_scheduled_tasks_filter_status(self, admin_client):
        """测试按状态筛选定时任务"""
        response = admin_client.get("/api/push/schedule/list?status=pending")
        assert response.status_code == 200
        data = response.json()
        for task in data["tasks"]:
            assert task["status"] == "pending"


class TestPushHistory:
    """推送历史测试"""
    
    def test_get_push_history(self, admin_client):
        """测试获取推送历史"""
        response = admin_client.get("/api/push/history")
        assert response.status_code == 200
        data = response.json()
        assert "records" in data
        assert "total" in data
    
    def test_get_push_history_filter_type(self, admin_client):
        """测试按类型筛选推送历史"""
        response = admin_client.get("/api/push/history?type=vote")
        assert response.status_code == 200
        data = response.json()
        for record in data["records"]:
            assert record["type"] == "vote"
    
    def test_get_push_history_filter_status(self, admin_client):
        """测试按状态筛选推送历史"""
        response = admin_client.get("/api/push/history?status=success")
        assert response.status_code == 200
        data = response.json()
        for record in data["records"]:
            assert record["status"] == "success"
    
    def test_get_push_detail(self, admin_client):
        """测试获取推送详情"""
        response = admin_client.get("/api/push/history/message_id_123")
        assert response.status_code == 200
        data = response.json()
        assert "message_id" in data
        assert "content" in data
        assert "sent_time" in data
        assert "status" in data


class TestPushStatistics:
    """推送统计测试"""
    
    def test_push_statistics(self, admin_client):
        """测试获取推送统计"""
        response = admin_client.get("/api/push/statistics")
        assert response.status_code == 200
        data = response.json()
        assert "total_sent" in data
        assert "success_rate" in data
        assert "failed_count" in data
    
    def test_push_statistics_by_type(self, admin_client):
        """测试按类型获取推送统计"""
        response = admin_client.get("/api/push/statistics?type=wechat")
        assert response.status_code == 200
        data = response.json()
        assert "wechat_sent" in data
        assert "wechat_success_rate" in data
    
    def test_push_statistics_by_date(self, admin_client):
        """测试按日期范围获取推送统计"""
        response = admin_client.get(
            "/api/push/statistics?start_date=2026-03-01&end_date=2026-03-31"
        )
        assert response.status_code == 200
        data = response.json()
        assert "daily_stats" in data
        assert isinstance(data["daily_stats"], list)


class TestUserNotificationSettings:
    """用户通知设置测试"""
    
    def test_get_notification_settings(self, client):
        """测试获取用户通知设置"""
        # 登录
        login_response = client.post(
            "/api/auth/wechat/login",
            json={"code": "test_code"}
        )
        token = login_response.json()["access_token"]
        
        response = client.get(
            "/api/push/settings",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "vote_notification" in data
        assert "meeting_notification" in data
        assert "system_notification" in data
    
    def test_update_notification_settings(self, client):
        """测试更新用户通知设置"""
        login_response = client.post(
            "/api/auth/wechat/login",
            json={"code": "test_code"}
        )
        token = login_response.json()["access_token"]
        
        response = client.put(
            "/api/push/settings",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "vote_notification": True,
                "meeting_notification": False,
                "system_notification": True,
                "sms_enabled": False,
                "wechat_enabled": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["meeting_notification"] is False
    
    def test_unsubscribe_all(self, client):
        """测试取消所有订阅"""
        login_response = client.post(
            "/api/auth/wechat/login",
            json={"code": "test_code"}
        )
        token = login_response.json()["access_token"]
        
        response = client.post(
            "/api/push/settings/unsubscribe",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
