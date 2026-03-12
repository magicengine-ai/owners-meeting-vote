"""
用户认证模块
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import logging
import httpx

from ..db import get_db
from ..config import settings
from .utils import (
    create_access_token,
    get_current_user,
    get_current_verified_user,
    get_password_hash,
    verify_password
)
from ..models import User

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== 数据模型 ====================

class WechatLoginRequest(BaseModel):
    """微信登录请求"""
    code: str = Field(..., description="微信登录 code")
    appid: Optional[str] = Field(None, description="小程序 AppID")


class PhoneLoginRequest(BaseModel):
    """手机号登录请求"""
    phone: str = Field(..., description="手机号")
    sms_code: str = Field(..., description="短信验证码")
    sms_token: Optional[str] = Field(None, description="短信 token（发送验证码时返回）")


class PhoneSmsRequest(BaseModel):
    """发送短信验证码请求"""
    phone: str = Field(..., description="手机号")
    captcha: Optional[str] = Field(None, description="图形验证码")


class PhoneSmsResponse(BaseModel):
    """发送短信验证码响应"""
    sms_token: str
    expire_seconds: int = 300
    message: str = "验证码已发送"


class WechatLoginResponse(BaseModel):
    """微信登录响应"""
    access_token: str
    token_type: str = "bearer"
    openid: str
    is_verified: bool = False
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None


class PropertyCertRequest(BaseModel):
    """房产证上传请求"""
    image_base64: str = Field(..., description="房产证图片 Base64")
    cert_type: str = Field(default="property", description="证件类型：property/fangben")


class PropertyCertResponse(BaseModel):
    """房产证识别响应"""
    owner_name: str
    cert_number: str
    address: str
    area: Optional[float]
    confidence: float


class VerifyStatusResponse(BaseModel):
    """认证状态响应"""
    status: str  # pending/rejected/approved
    message: str
    verified_at: Optional[str]


# ==================== 认证流程 ====================

@router.post("/wechat/login", response_model=WechatLoginResponse)
async def wechat_login(request: WechatLoginRequest, db: Session = Depends(get_db)):
    """
    微信授权登录
    
    1. 使用 code 换取 openid
    2. 创建或更新用户记录
    3. 返回 JWT token
    """
    logger.info(f"微信登录请求：code={request.code}")
    
    # 1. 调用微信 API 换取 openid
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.weixin.qq.com/sns/jscode2session",
                params={
                    "appid": settings.WECHAT_APP_ID,
                    "secret": settings.WECHAT_APP_SECRET,
                    "js_code": request.code,
                    "grant_type": "authorization_code"
                },
                timeout=10.0
            )
            response.raise_for_status()
            wechat_data = response.json()
            
            if "errcode" in wechat_data:
                logger.error(f"微信登录失败：{wechat_data}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"微信登录失败：{wechat_data.get('errmsg', 'Unknown error')}"
                )
            
            openid = wechat_data.get("openid")
            session_key = wechat_data.get("session_key")
            
    except httpx.RequestError as e:
        logger.error(f"微信 API 请求失败：{str(e)}")
        # 开发环境允许模拟登录
        if settings.DEBUG:
            openid = f"dev_openid_{request.code}"
            session_key = "dev_session_key"
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="微信服务暂时不可用"
            )
    
    # 2. 查询或创建用户
    user = db.query(User).filter(User.openid == openid).first()
    
    if not user:
        # 创建新用户
        user = User(
            openid=openid,
            is_verified=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"创建新用户：openid={openid}")
    else:
        # 更新用户信息
        user.updated_at = datetime.now()
        db.commit()
        logger.info(f"用户登录：openid={openid}")
    
    # 3. 生成 JWT token
    access_token = create_access_token(
        data={"sub": openid, "user_id": user.id}
    )
    
    return WechatLoginResponse(
        access_token=access_token,
        token_type="bearer",
        openid=openid,
        is_verified=user.is_verified,
        nickname=user.nickname,
        avatar_url=user.avatar_url,
        phone=user.phone
    )


# ==================== 短信验证码 ====================

# 内存存储验证码（生产环境应该用 Redis）
_sms_code_store = {}


@router.post("/phone/sms", response_model=PhoneSmsResponse)
async def send_phone_sms(request: PhoneSmsRequest):
    """
    发送短信验证码
    
    1. 验证手机号格式
    2. 生成 6 位验证码
    3. 发送短信（开发环境打印验证码）
    4. 返回 sms_token 用于验证
    """
    logger.info(f"发送短信验证码：phone={request.phone}")
    
    # 验证手机号格式
    import re
    if not re.match(r"^1[3-9]\d{9}$", request.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号格式不正确"
        )
    
    # 生成验证码和 token
    import random
    import string
    sms_code = "".join(random.choices(string.digits, k=6))
    sms_token = "".join(random.choices(string.ascii_letters + string.digits, k=32))
    
    # 存储验证码（5 分钟有效期）
    _sms_code_store[sms_token] = {
        "code": sms_code,
        "phone": request.phone,
        "expire_at": datetime.now().timestamp() + 300
    }
    
    # 发送短信（开发环境打印）
    if settings.DEBUG:
        logger.info(f"【验证码】{sms_code}（开发环境，实际应发送短信）")
    else:
        # TODO: 调用短信服务商 API
        # 阿里云/腾讯云短信服务
        pass
    
    return PhoneSmsResponse(
        sms_token=sms_token,
        expire_seconds=300,
        message="验证码已发送"
    )


@router.post("/phone/login", response_model=WechatLoginResponse)
async def phone_login(request: PhoneLoginRequest, db: Session = Depends(get_db)):
    """
    手机号登录
    
    1. 验证短信验证码
    2. 查询或创建用户
    3. 返回 JWT token
    """
    logger.info(f"手机号登录请求：phone={request.phone}")
    
    # 1. 验证短信验证码
    sms_data = _sms_code_store.get(request.sms_token)
    if not sms_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码已过期，请重新获取"
        )
    
    if sms_data["phone"] != request.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号不匹配"
        )
    
    if sms_data["expire_at"] < datetime.now().timestamp():
        # 清理过期验证码
        del _sms_code_store[request.sms_token]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码已过期"
        )
    
    if sms_data["code"] != request.sms_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误"
        )
    
    # 验证成功，清理验证码
    del _sms_code_store[request.sms_token]
    
    # 2. 查询或创建用户
    user = db.query(User).filter(User.phone == request.phone).first()
    
    if not user:
        # 创建新用户（需要 openid，这里生成一个临时 openid）
        import hashlib
        temp_openid = f"phone_{hashlib.sha256(request.phone.encode()).hexdigest()[:32]}"
        user = User(
            openid=temp_openid,
            phone=request.phone,
            is_verified=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"创建新用户：phone={request.phone}")
    else:
        # 更新用户信息
        user.updated_at = datetime.now()
        db.commit()
        logger.info(f"用户登录：phone={request.phone}")
    
    # 3. 生成 JWT token
    access_token = create_access_token(
        data={"sub": user.openid, "user_id": user.id}
    )
    
    return WechatLoginResponse(
        access_token=access_token,
        token_type="bearer",
        openid=user.openid,
        is_verified=user.is_verified,
        nickname=user.nickname,
        avatar_url=user.avatar_url,
        phone=user.phone
    )


@router.post("/property/ocr", response_model=PropertyCertResponse)
async def property_ocr(request: PropertyCertRequest, db: Session = Depends(get_db)):
    """
    房产证 OCR 识别
    
    1. 调用百度 AI OCR 接口
    2. 提取关键信息（产权人、地址、面积等）
    3. 返回识别结果
    """
    # TODO: 实现 OCR 识别逻辑
    # 1. 调用百度 AI OCR API
    # 2. 解析返回结果
    # 3. 返回结构化数据
    
    logger.info(f"房产证 OCR 请求：cert_type={request.cert_type}")
    
    # 模拟响应
    return PropertyCertResponse(
        owner_name="张三",
        cert_number="京 (2024) 朝阳区不动产权第 1234567 号",
        address="北京市朝阳区 XX 路 XX 号院 X 号楼 X 单元 XXX 室",
        area=89.5,
        confidence=0.95
    )


@router.post("/property/verify")
async def verify_property(
    owner_name: str,
    cert_number: str,
    address: str,
    db: Session = Depends(get_db)
):
    """
    房产证验证
    
    1. 对接政府系统验证房产证真伪
    2. 验证产权人信息
    3. 验证房屋地址
    """
    # TODO: 实现政府系统对接
    # 1. 调用住建委/房管局 API
    # 2. 验证房产证信息
    # 3. 返回验证结果
    
    logger.info(f"房产证验证：name={owner_name}, cert={cert_number}")
    
    return {"status": "approved", "message": "验证通过"}


@router.post("/face/recognize")
async def face_recognition(
    image_base64: str,
    openid: str,
    db: Session = Depends(get_db)
):
    """
    人脸识别
    
    1. 调用人脸识别 API
    2. 与公安系统照片比对
    3. 返回识别结果
    """
    # TODO: 实现人脸识别逻辑
    
    logger.info(f"人脸识别：openid={openid}")
    
    return {"status": "approved", "confidence": 0.98}


@router.get("/me", response_model=WechatLoginResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户信息
    
    需要携带有效的 JWT token
    """
    # 生成新的 token（续期）
    access_token = create_access_token(
        data={"sub": current_user.openid, "user_id": current_user.id}
    )
    
    return WechatLoginResponse(
        access_token=access_token,
        token_type="bearer",
        openid=current_user.openid,
        is_verified=current_user.is_verified,
        nickname=current_user.nickname,
        avatar_url=current_user.avatar_url
    )


@router.get("/verify/status", response_model=VerifyStatusResponse)
async def get_verify_status(
    current_user: User = Depends(get_current_user)
):
    """
    查询认证状态
    
    需要携带有效的 JWT token
    """
    if current_user.is_verified:
        return VerifyStatusResponse(
            status="approved",
            message="认证通过",
            verified_at=current_user.verified_at.isoformat() if current_user.verified_at else None
        )
    elif current_user.verification_reject_reason:
        return VerifyStatusResponse(
            status="rejected",
            message=f"认证被拒绝：{current_user.verification_reject_reason}"
        )
    else:
        return VerifyStatusResponse(
            status="pending",
            message="认证审核中"
        )


@router.post("/bind/building")
async def bind_building_info(
    openid: str,
    building_id: str,
    unit_id: str,
    room_id: str,
    db: Session = Depends(get_db)
):
    """
    绑定楼栋信息
    
    将用户与具体的楼栋、单元、房间绑定
    """
    # TODO: 实现楼栋绑定逻辑
    
    logger.info(f"绑定楼栋：openid={openid}, building={building_id}")
    
    return {"status": "success", "message": "绑定成功"}
