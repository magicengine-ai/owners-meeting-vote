"""
微信模板消息推送
"""
import httpx
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from ..config import settings

logger = logging.getLogger(__name__)


class WechatTemplateSender:
    """微信模板消息发送器"""
    
    def __init__(self):
        self.appid = settings.WECHAT_APP_ID
        self.secret = settings.WECHAT_APP_SECRET
        self.access_token = None
        self.token_expires_at = None
    
    async def get_access_token(self) -> str:
        """获取微信 access token"""
        # 如果 token 有效，直接返回
        if self.access_token and self.token_expires_at and self.token_expires_at > datetime.now():
            return self.access_token
        
        # 获取新 token
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.weixin.qq.com/cgi-bin/token",
                params={
                    "grant_type": "client_credential",
                    "appid": self.appid,
                    "secret": self.secret
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            if "errcode" in data:
                raise Exception(f"获取微信 token 失败：{data.get('errmsg', 'Unknown error')}")
            
            self.access_token = data["access_token"]
            self.token_expires_at = datetime.now().replace(second=0, microsecond=0)
            
            # token 有效期 7200 秒，提前 5 分钟刷新
            from datetime import timedelta
            self.token_expires_at += timedelta(seconds=7200 - 300)
            
            return self.access_token
    
    async def send_template_message(
        self,
        openid: str,
        template_id: str,
        page: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        color: Optional[str] = "#173177"
    ) -> bool:
        """
        发送模板消息
        
        Args:
            openid: 用户 openid
            template_id: 模板 ID
            page: 点击消息跳转的页面
            data: 模板数据
            color: 主色调
            
        Returns:
            是否发送成功
        """
        try:
            access_token = await self.get_access_token()
            
            # 构建消息体
            message = {
                "touser": openid,
                "template_id": template_id,
                "page": page or "",
                "data": data or {},
                "color": color
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}",
                    json=message,
                    timeout=10.0
                )
                response.raise_for_status()
                result = response.json()
                
                if result.get("errcode", 0) == 0:
                    logger.info(f"模板消息发送成功：openid={openid}, template_id={template_id}")
                    return True
                else:
                    logger.error(f"模板消息发送失败：{result.get('errmsg', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            logger.error(f"发送模板消息异常：{str(e)}", exc_info=True)
            return False
    
    async def send_verify_approved(
        self,
        openid: str,
        verify_time: str
    ) -> bool:
        """
        发送认证通过通知
        
        需要在微信公众平台配置模板：
        模板标题：认证通过通知
        模板 ID：在微信公众平台获取
        """
        template_id = "YOUR_VERIFY_APPROVED_TEMPLATE_ID"  # 替换为实际模板 ID
        
        data = {
            "thing1": {"value": "业主身份认证"},
            "thing2": {"value": "认证已通过"},
            "time3": {"value": verify_time},
            "thing4": {"value": "现在您可以参与小区投票和会议了"}
        }
        
        return await self.send_template_message(
            openid=openid,
            template_id=template_id,
            page="/pages/profile/profile",
            data=data
        )
    
    async def send_verify_rejected(
        self,
        openid: str,
        reason: str,
        verify_time: str
    ) -> bool:
        """
        发送认证拒绝通知
        
        需要在微信公众平台配置模板：
        模板标题：认证审核通知
        模板 ID：在微信公众平台获取
        """
        template_id = "YOUR_VERIFY_REJECTED_TEMPLATE_ID"  # 替换为实际模板 ID
        
        data = {
            "thing1": {"value": "业主身份认证"},
            "thing2": {"value": "认证未通过"},
            "thing3": {"value": reason},
            "time4": {"value": verify_time},
            "thing5": {"value": "请修改后重新提交"}
        }
        
        return await self.send_template_message(
            openid=openid,
            template_id=template_id,
            page="/pages/auth/verify/verify",
            data=data
        )
    
    async def send_vote_notice(
        self,
        openid: str,
        vote_title: str,
        vote_deadline: str
    ) -> bool:
        """
        发送投票通知
        
        需要在微信公众平台配置模板：
        模板标题：投票通知
        模板 ID：在微信公众平台获取
        """
        template_id = "YOUR_VOTE_NOTICE_TEMPLATE_ID"  # 替换为实际模板 ID
        
        data = {
            "thing1": {"value": vote_title},
            "time2": {"value": vote_deadline},
            "thing3": {"value": "请点击查看详情并投票"}
        }
        
        return await self.send_template_message(
            openid=openid,
            template_id=template_id,
            page="/pages/vote/detail",
            data=data
        )


# 全局实例
wechat_sender = WechatTemplateSender()


# ==================== 便捷函数 ====================

async def notify_verify_approved(openid: str, verify_time: str) -> bool:
    """发送认证通过通知"""
    return await wechat_sender.send_verify_approved(openid, verify_time)


async def notify_verify_rejected(openid: str, reason: str, verify_time: str) -> bool:
    """发送认证拒绝通知"""
    return await wechat_sender.send_verify_rejected(openid, reason, verify_time)


async def notify_vote(openid: str, vote_title: str, vote_deadline: str) -> bool:
    """发送投票通知"""
    return await wechat_sender.send_vote_notice(openid, vote_title, vote_deadline)
