"""
微信原生鉴权中间件
利用云托管自动注入的 X-WX-OPENID 和 X-WX-UNIONID
"""
from fastapi import Request, HTTPException, Depends
from typing import Optional, Dict
import jwt
from datetime import datetime, timedelta
from ..config import settings


class WeChatAuth:
    """微信鉴权类"""
    
    @staticmethod
    def get_user_info_from_headers(request: Request) -> Dict:
        """
        从请求头获取微信用户信息
        
        云托管环境：自动注入 X-WX-OPENID 和 X-WX-UNIONID
        本地开发环境：从 JWT Token 获取
        
        Returns:
            dict: {
                "openid": str,      # 用户 OpenID
                "unionid": str,     # 用户 UnionID（可选）
                "is_verified": bool,  # 是否已验证
                "source": str       # 来源：wechat_cloud / jwt / local_dev
            }
        """
        # 尝试从云托管注入的请求头获取
        openid = request.headers.get("X-WX-OPENID")
        unionid = request.headers.get("X-WX-UNIONID")
        
        if openid:
            return {
                "openid": openid,
                "unionid": unionid,
                "is_verified": True,
                "source": "wechat_cloud"
            }
        
        # 本地开发环境：从 JWT Token 获取
        return WeChatAuth.get_user_from_jwt(request)
    
    @staticmethod
    def get_user_from_jwt(request: Request) -> Dict:
        """
        本地开发环境：从 JWT Token 获取用户信息
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {
                "openid": None,
                "unionid": None,
                "is_verified": False,
                "source": "local_dev"
            }
        
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return {
                "openid": payload.get("sub"),
                "unionid": payload.get("unionid"),
                "is_verified": True,
                "source": "jwt"
            }
        except jwt.InvalidTokenError:
            return {
                "openid": None,
                "unionid": None,
                "is_verified": False,
                "source": "invalid_token"
            }


# ==================== 依赖注入函数 ====================

async def get_current_user(request: Request) -> Dict:
    """
    获取当前登录用户信息（强制登录）
    
    用法:
        @app.get("/api/user/profile")
        async def get_profile(current_user: Dict = Depends(get_current_user)):
            return {"openid": current_user["openid"]}
    """
    user_info = WeChatAuth.get_user_info_from_headers(request)
    
    if not user_info["openid"]:
        raise HTTPException(
            status_code=401,
            detail="未登录或登录已过期",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user_info


async def get_optional_user(request: Request) -> Dict:
    """
    获取当前用户信息（可选，未登录返回 None）
    
    用法:
        @app.get("/api/public/info")
        async def get_info(current_user: Dict = Depends(get_optional_user)):
            if current_user["openid"]:
                return {"message": f"你好，{current_user['openid']}"}
            return {"message": "游客模式"}
    """
    return WeChatAuth.get_user_info_from_headers(request)


async def get_admin_user(request: Request) -> Dict:
    """
    获取管理员用户信息（需要管理员权限）
    
    用法:
        @app.post("/api/admin/vote/create")
        async def create_vote(
            vote_data: VoteCreate,
            current_user: Dict = Depends(get_admin_user)
        ):
            # 只有管理员可以访问
            pass
    """
    from ..src.db import get_db
    from ..src.models import User
    
    user_info = await get_current_user(request)
    openid = user_info["openid"]
    
    # 检查是否为管理员
    db = next(get_db())
    try:
        user = db.query(User).filter(User.openid == openid).first()
        if not user or not user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="需要管理员权限"
            )
        return user_info
    finally:
        db.close()
