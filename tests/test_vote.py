"""
投票模块测试用例
测试投票创建、提交、统计等功能
"""
import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time


class TestCreateVote:
    """创建投票测试"""
    
    def test_create_vote_success(self, admin_client):
        """测试创建投票成功（管理员）"""
        now = datetime.now()
        response = admin_client.post(
            "/api/vote/create",
            json={
                "title": "关于小区绿化改造的投票",
                "description": "是否同意对小区进行绿化改造",
                "start_time": now.isoformat(),
                "end_time": (now + timedelta(days=7)).isoformat(),
                "options": ["赞成", "反对", "弃权"],
                "vote_type": "single"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "vote_id" in data
        assert data["title"] == "关于小区绿化改造的投票"
        assert len(data["options"]) == 3
    
    def test_create_vote_multi_type(self, admin_client):
        """测试创建多选投票"""
        now = datetime.now()
        response = admin_client.post(
            "/api/vote/create",
            json={
                "title": "业委会委员选举",
                "description": "请选择您支持的委员候选人（可多选）",
                "start_time": now.isoformat(),
                "end_time": (now + timedelta(days=14)).isoformat(),
                "options": ["张三", "李四", "王五", "赵六"],
                "vote_type": "multi",
                "max_choices": 2
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["vote_type"] == "multi"
        assert data["max_choices"] == 2
    
    def test_create_vote_unauthorized(self, client):
        """测试创建投票 - 未授权"""
        now = datetime.now()
        response = client.post(
            "/api/vote/create",
            json={
                "title": "测试投票",
                "description": "测试",
                "start_time": now.isoformat(),
                "end_time": (now + timedelta(days=7)).isoformat(),
                "options": ["赞成", "反对"],
                "vote_type": "single"
            }
        )
        assert response.status_code == 401
    
    def test_create_vote_not_admin(self, client, test_user):
        """测试创建投票 - 普通用户无权限"""
        # 普通用户登录
        login_response = client.post(
            "/api/auth/wechat/login",
            json={"code": "test_code"}
        )
        token = login_response.json()["access_token"]
        
        now = datetime.now()
        response = client.post(
            "/api/vote/create",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "测试投票",
                "description": "测试",
                "start_time": now.isoformat(),
                "end_time": (now + timedelta(days=7)).isoformat(),
                "options": ["赞成", "反对"],
                "vote_type": "single"
            }
        )
        assert response.status_code == 403
    
    def test_create_vote_invalid_time(self, admin_client):
        """测试创建投票 - 结束时间早于开始时间"""
        now = datetime.now()
        response = admin_client.post(
            "/api/vote/create",
            json={
                "title": "测试投票",
                "description": "测试",
                "start_time": (now + timedelta(days=7)).isoformat(),
                "end_time": now.isoformat(),  # 结束时间早于开始时间
                "options": ["赞成", "反对"],
                "vote_type": "single"
            }
        )
        assert response.status_code == 400
        assert "结束时间必须晚于开始时间" in response.json()["detail"]
    
    def test_create_vote_few_options(self, admin_client):
        """测试创建投票 - 选项少于 2 个"""
        now = datetime.now()
        response = admin_client.post(
            "/api/vote/create",
            json={
                "title": "测试投票",
                "description": "测试",
                "start_time": now.isoformat(),
                "end_time": (now + timedelta(days=7)).isoformat(),
                "options": ["赞成"],  # 只有 1 个选项
                "vote_type": "single"
            }
        )
        assert response.status_code == 400


class TestVoteList:
    """投票列表测试"""
    
    def test_vote_list_success(self, client):
        """测试获取投票列表"""
        response = client.get("/api/vote/list")
        assert response.status_code == 200
        data = response.json()
        assert "votes" in data
        assert "total" in data
        assert isinstance(data["votes"], list)
    
    def test_vote_list_filter_status(self, client):
        """测试按状态筛选投票列表"""
        # 获取进行中的投票
        response = client.get("/api/vote/list?status=ongoing")
        assert response.status_code == 200
        data = response.json()
        for vote in data["votes"]:
            assert vote["status"] == "ongoing"
    
    def test_vote_list_pagination(self, client):
        """测试投票列表分页"""
        response = client.get("/api/vote/list?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data


class TestVoteDetail:
    """投票详情测试"""
    
    def test_vote_detail_success(self, client, vote_id):
        """测试获取投票详情"""
        response = client.get(f"/api/vote/detail/{vote_id}")
        assert response.status_code == 200
        data = response.json()
        assert "vote_id" in data
        assert "title" in data
        assert "options" in data
        assert "start_time" in data
        assert "end_time" in data
    
    def test_vote_detail_not_found(self, client):
        """测试获取不存在的投票详情"""
        response = client.get("/api/vote/detail/non_existent_id")
        assert response.status_code == 404


class TestSubmitVote:
    """提交投票测试"""
    
    def test_submit_vote_success(self, client, vote_id):
        """测试提交投票成功"""
        response = client.post(
            "/api/vote/submit",
            json={
                "vote_id": vote_id,
                "options": ["赞成"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "vote_record_id" in data
    
    def test_submit_vote_not_verified(self, client, vote_id):
        """测试提交投票 - 用户未认证"""
        # 登录未认证用户
        login_response = client.post(
            "/api/auth/wechat/login",
            json={"code": "test_code_unverified"}
        )
        token = login_response.json()["access_token"]
        
        response = client.post(
            "/api/vote/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "vote_id": vote_id,
                "options": ["赞成"]
            }
        )
        assert response.status_code == 403
        assert "未认证用户不能投票" in response.json()["detail"]
    
    def test_submit_vote_duplicate(self, client, vote_id):
        """测试重复投票"""
        # 第一次投票
        response1 = client.post(
            "/api/vote/submit",
            json={
                "vote_id": vote_id,
                "options": ["赞成"]
            }
        )
        assert response1.status_code == 200
        
        # 第二次投票
        response2 = client.post(
            "/api/vote/submit",
            json={
                "vote_id": vote_id,
                "options": ["反对"]
            }
        )
        assert response2.status_code == 400
        assert "您已经投过票了" in response2.json()["detail"]
    
    def test_submit_vote_invalid_option(self, client, vote_id):
        """测试提交无效选项"""
        response = client.post(
            "/api/vote/submit",
            json={
                "vote_id": vote_id,
                "options": ["无效选项"]
            }
        )
        assert response.status_code == 400
        assert "无效的投票选项" in response.json()["detail"]
    
    def test_submit_vote_expired(self, client, vote_id):
        """测试投票已过期"""
        with freeze_time("2026-03-25 23:59:59"):  # 假设投票已结束
            response = client.post(
                "/api/vote/submit",
                json={
                    "vote_id": vote_id,
                    "options": ["赞成"]
                }
            )
            assert response.status_code == 400
            assert "投票已结束" in response.json()["detail"]
    
    def test_submit_vote_not_started(self, client, vote_id):
        """测试投票未开始"""
        with freeze_time("2026-03-10 00:00:00"):  # 假设投票未开始
            response = client.post(
                "/api/vote/submit",
                json={
                    "vote_id": vote_id,
                    "options": ["赞成"]
                }
            )
            assert response.status_code == 400
            assert "投票尚未开始" in response.json()["detail"]


class TestVoteResult:
    """投票结果测试"""
    
    def test_vote_result_success(self, client, vote_id):
        """测试获取投票结果"""
        response = client.get(f"/api/vote/result/{vote_id}")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total_votes" in data
        assert "option_stats" in data
    
    def test_vote_result_real_time(self, client, vote_id):
        """测试投票结果实时更新"""
        # 先投几票
        client.post(
            "/api/vote/submit",
            json={"vote_id": vote_id, "options": ["赞成"]}
        )
        client.post(
            "/api/vote/submit",
            json={"vote_id": vote_id, "options": ["反对"]}
        )
        
        # 获取结果
        response = client.get(f"/api/vote/result/{vote_id}")
        data = response.json()
        assert data["total_votes"] >= 2


class TestVoteStatistics:
    """投票统计测试"""
    
    def test_vote_statistics(self, admin_client, vote_id):
        """测试获取投票统计（管理员）"""
        response = admin_client.get(f"/api/vote/statistics/{vote_id}")
        assert response.status_code == 200
        data = response.json()
        assert "total_voters" in data
        assert "participation_rate" in data
        assert "option_distribution" in data
    
    def test_vote_export_results(self, admin_client, vote_id):
        """测试导出投票结果（管理员）"""
        response = admin_client.post(
            f"/api/vote/export/{vote_id}",
            json={"format": "csv"}
        )
        assert response.status_code == 200
        assert "download_url" in response.json()


class TestDelegateVote:
    """委托投票测试"""
    
    def test_create_delegate(self, client, test_user):
        """测试创建委托"""
        # 登录
        login_response = client.post(
            "/api/auth/wechat/login",
            json={"code": "test_code"}
        )
        token = login_response.json()["access_token"]
        
        response = client.post(
            "/api/vote/delegate/create",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "delegate_to": "other_user_openid",
                "vote_scope": "all"  # 委托所有投票
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "delegate_id" in data
    
    def test_revoke_delegate(self, client):
        """测试撤销委托"""
        login_response = client.post(
            "/api/auth/wechat/login",
            json={"code": "test_code"}
        )
        token = login_response.json()["access_token"]
        
        response = client.post(
            "/api/vote/delegate/revoke",
            headers={"Authorization": f"Bearer {token}"},
            json={"delegate_id": "test_delegate_id"}
        )
        assert response.status_code == 200
    
    def test_vote_with_delegate(self, client, vote_id):
        """测试代理人投票"""
        login_response = client.post(
            "/api/auth/wechat/login",
            json={"code": "test_code"}
        )
        token = login_response.json()["access_token"]
        
        # 代理人投票
        response = client.post(
            "/api/vote/submit",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "vote_id": vote_id,
                "options": ["赞成"],
                "is_delegate": True,
                "delegate_id": "test_delegate_id"
            }
        )
        assert response.status_code == 200
