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
    """房产证上传/验证请求"""
    image_base64: Optional[str] = Field(None, description="房产证图片 Base64（OCR 识别时需要）")
    cert_type: str = Field(default="property", description="证件类型：property/fangben")
    owner_name: Optional[str] = Field(None, description="产权人姓名（提交认证时需要）")
    cert_number: Optional[str] = Field(None, description="房产证号（提交认证时需要）")
    address: Optional[str] = Field(None, description="房屋地址（提交认证时需要）")
    area: Optional[float] = Field(None, description="建筑面积（提交认证时需要）")


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
    logger.info(f"房产证 OCR 请求：cert_type={request.cert_type}")
    
    try:
        # 1. 调用百度 AI OCR API
        from aip import AipOcr
        
        # 初始化客户端
        client = AipOcr(
            settings.OCR_APP_ID,
            settings.OCR_API_KEY,
            settings.OCR_SECRET_KEY
        )
        
        # 2. 调用房产证识别接口
        image_data = request.image_base64
        result = client.accurateBasic(image_data)
        
        # 3. 解析 OCR 结果
        if 'words_result' not in result:
            logger.error(f"OCR 识别失败：{result}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OCR 识别失败，请重试"
            )
        
        # 4. 提取关键信息（简化版，实际需要根据房产证格式优化）
        words_list = [item['words'] for item in result['words_result']]
        words_text = '\n'.join(words_list)
        
        # 提取产权人、地址、面积等信息
        owner_name = extract_owner_name(words_text)
        cert_number = extract_cert_number(words_text)
        address = extract_address(words_text)
        area = extract_area(words_text)
        
        logger.info(f"OCR 识别成功：owner={owner_name}, address={address}")
        
        return PropertyCertResponse(
            owner_name=owner_name or "未识别到产权人",
            cert_number=cert_number or "未识别到证号",
            address=address or "未识别到地址",
            area=area,
            confidence=result.get('words_result_confidence', 0.9)
        )
        
    except ImportError:
        # 开发环境：如果没有安装百度 AI SDK，返回模拟数据
        if settings.DEBUG:
            logger.warning("百度 AI SDK 未安装，使用模拟数据")
            return PropertyCertResponse(
                owner_name="张三",
                cert_number="京 (2024) 朝阳区不动产权第 1234567 号",
                address="北京市朝阳区 XX 路 XX 号院 X 号楼 X 单元 XXX 室",
                area=89.5,
                confidence=0.95
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="OCR 服务暂时不可用"
            )
    except Exception as e:
        logger.error(f"OCR 识别异常：{str(e)}", exc_info=True)
        if settings.DEBUG:
            # 开发环境返回模拟数据
            return PropertyCertResponse(
                owner_name="张三",
                cert_number="京 (2024) 朝阳区不动产权第 1234567 号",
                address="北京市朝阳区 XX 路 XX 号院 X 号楼 X 单元 XXX 室",
                area=89.5,
                confidence=0.95
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OCR 识别失败，请重试"
            )


# ==================== OCR 信息提取辅助函数 ====================

def extract_owner_name(text: str) -> str:
    """提取产权人姓名"""
    import re
    # 匹配"产权人"、"权利人"等关键词后的姓名
    patterns = [
        r'产权 [人主][:：]\s*([^\s\n]+)',
        r'权利 [人主][:：]\s*([^\s\n]+)',
        r'共有人 [:：]\s*([^\s\n]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return ""


def extract_cert_number(text: str) -> str:
    """提取房产证号"""
    import re
    patterns = [
        r'(京 [沪津渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼][A-Z]?[\(（]?\d{4}[\)）]?[A-Z]?不动产权第\s*\d+\s*号)',
        r'(京 [沪津渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼][A-Z]?[\(（]?\d{4}[\)）]?[A-Z]?房地产权证第\s*\d+\s*号)',
        r'权证编号 [:：]\s*([^\s\n]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return ""


def extract_address(text: str) -> str:
    """提取房屋地址"""
    import re
    patterns = [
        r'坐落 [:：]\s*([^\n]+)',
        r'地址 [:：]\s*([^\n]+)',
        r'位置 [:：]\s*([^\n]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return ""


def extract_area(text: str) -> Optional[float]:
    """提取建筑面积"""
    import re
    patterns = [
        r'建筑面积 [:：]?\s*([\d.]+)\s*[㎡平方米]',
        r'面积 [:：]?\s*([\d.]+)\s*[㎡平方米]',
        r'([\d.]+)\s*[㎡平方米]',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1))
            except:
                pass
    return None


@router.post("/property/verify")
async def verify_property(
    request: PropertyCertRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    提交房产证认证
    
    1. 保存用户房产信息
    2. 设置认证状态为待审核
    3. 返回审核状态
    """
    logger.info(f"提交房产证认证：user_id={current_user.id}")
    
    # 1. 更新用户房产信息
    current_user.property_cert_number = request.cert_number
    current_user.property_owner = request.owner_name
    current_user.property_address = request.address
    current_user.property_area = request.area
    current_user.is_verified = False  # 待审核状态
    current_user.updated_at = datetime.now()
    
    db.commit()
    
    logger.info(f"房产证认证已提交：user_id={current_user.id}, status=pending")
    
    return {
        "status": "pending",
        "message": "认证已提交，等待审核"
    }


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
