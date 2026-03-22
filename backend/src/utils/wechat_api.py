"""
微信 API 调用工具（免鉴权）
利用云托管的 X-WX-APPID 和 X-WX-SECRET 注入

云托管优势：
- 无需维护 access_token
- 无需证书调用微信支付
- 自动处理签名验证
"""
import httpx
from typing import Optional, Dict, Any
from ..config import settings


class WeChatAPI:
    """微信 API 调用工具类"""
    
    BASE_URL = "https://api.weixin.qq.com"
    
    @classmethod
    async def request(
        cls,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        调用微信 API（免鉴权）
        
        云托管会自动注入：
        - X-WX-APPID: 小程序 AppID
        - X-WX-SECRET: 小程序 AppSecret
        
        无需手动维护 access_token！
        
        Args:
            method: HTTP 方法（GET/POST）
            endpoint: API 端点（如 /cgi-bin/message/subscribe/send）
            json_data: 请求体
            params: 查询参数
        
        Returns:
            dict: 微信 API 响应
        
        Raises:
            Exception: API 调用失败时抛出异常
        """
        url = f"{cls.BASE_URL}{endpoint}"
        
        # 微信云托管环境：禁用 SSL 验证
        async with httpx.AsyncClient(
            timeout=30.0,
            verify=False
        ) as client:
            response = await client.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                headers={
                    # 云托管会自动使用这些值进行鉴权
                    "X-WX-APPID": settings.WECHAT_APP_ID,
                    "X-WX-SECRET": settings.WECHAT_APP_SECRET
                }
            )
            
            result = response.json()
            
            # 检查微信 API 错误码
            if result.get("errcode", 0) != 0:
                raise Exception(
                    f"微信 API 调用失败：{result.get('errmsg', 'Unknown error')} "
                    f"[errcode: {result.get('errcode')}]"
                )
            
            return result
    
    # ==================== 消息推送 ====================
    
    @classmethod
    async def send_subscribe_message(
        cls,
        openid: str,
        template_id: str,
        data: Dict,
        page: str = None
    ) -> Dict:
        """
        发送订阅消息
        
        Args:
            openid: 用户 OpenID
            template_id: 消息模板 ID（在微信公众平台申请）
            data: 消息数据（格式参考微信文档）
            page: 点击消息跳转的小程序页面
        
        Returns:
            dict: {"errcode": 0, "errmsg": "ok"}
        
        示例:
            await WeChatAPI.send_subscribe_message(
                openid="oXXXX",
                template_id="XXXX",
                data={
                    "thing1": {"value": "投票标题"},
                    "time2": {"value": "2026-03-22 10:00"},
                    "thing3": {"value": "请尽快参与投票"}
                },
                page="/pages/vote/detail?id=123"
            )
        """
        payload = {
            "touser": openid,
            "template_id": template_id,
            "data": data,
        }
        
        if page:
            payload["page"] = page
        
        return await cls.request(
            method="POST",
            endpoint="/cgi-bin/message/subscribe/send",
            json_data=payload
        )
    
    @classmethod
    async def send_uniform_message(
        cls,
        openid: str,
        template_id: str,
        data: Dict,
        page: str = None,
        miniprogram: Dict = None
    ) -> Dict:
        """
        发送统一服务消息（公众号 + 小程序）
        
        Args:
            openid: 用户 OpenID
            template_id: 模板 ID
            data: 消息数据
            page: 小程序页面
            miniprogram: 小程序信息
        """
        payload = {
            "touser": openid,
            "template_id": template_id,
            "data": data,
        }
        
        if page:
            payload["page"] = page
        
        if miniprogram:
            payload["miniprogram"] = miniprogram
        
        return await cls.request(
            method="POST",
            endpoint="/cgi-bin/message/wxopen/template/send",
            json_data=payload
        )
    
    # ==================== 用户信息 ====================
    
    @classmethod
    async def get_phone_number(
        cls,
        code: str
    ) -> Dict:
        """
        获取用户手机号（需要用户授权）
        
        Args:
            code: 小程序 getPhoneNumber 返回的 code
        
        Returns:
            dict: {
                "phone_number": "13800138000",
                "pure_phone_number": "13800138000",
                "country_code": "86",
                "watermark": {...}
            }
        """
        return await cls.request(
            method="POST",
            endpoint="/wxa/business/getuserphonenumber",
            json_data={"code": code}
        )
    
    @classmethod
    async def code_to_session(
        cls,
        js_code: str
    ) -> Dict:
        """
        登录凭证校验（小程序登录）
        
        Args:
            js_code: 小程序 wx.login() 返回的 code
        
        Returns:
            dict: {
                "openid": "xxx",
                "session_key": "xxx",
                "unionid": "xxx" (如果绑定)
            }
        """
        params = {
            "appid": settings.WECHAT_APP_ID,
            "secret": settings.WECHAT_APP_SECRET,
            "js_code": js_code,
            "grant_type": "authorization_code"
        }
        
        return await cls.request(
            method="GET",
            endpoint="/sns/jscode2session",
            params=params
        )
    
    # ==================== AccessToken 管理 ====================
    # 注意：云托管环境下通常不需要手动获取 access_token
    # 但某些接口仍需要，保留此方法
    
    @classmethod
    async def get_access_token(cls) -> str:
        """
        获取 access_token（云托管环境通常不需要）
        
        Returns:
            str: access_token
        """
        params = {
            "grant_type": "client_credential",
            "appid": settings.WECHAT_APP_ID,
            "secret": settings.WECHAT_APP_SECRET
        }
        
        result = await cls.request(
            method="GET",
            endpoint="/cgi-bin/token",
            params=params
        )
        
        return result.get("access_token")
