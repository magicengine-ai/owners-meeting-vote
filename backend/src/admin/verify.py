"""
管理员认证审核模块
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import logging

from ..db import get_db
from ..models import User
from ..auth.utils import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== 数据模型 ====================

class VerifyUserItem(BaseModel):
    """待审核用户信息"""
    user_id: int
    openid: str
    nickname: Optional[str]
    phone: Optional[str]
    property_owner: str
    property_cert_number: str
    property_address: str
    property_area: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


class VerifyUserListResponse(BaseModel):
    """待审核用户列表响应"""
    total: int
    users: List[VerifyUserItem]


class VerifyApproveRequest(BaseModel):
    """审核通过请求"""
    user_id: int
    remark: Optional[str] = None


class VerifyRejectRequest(BaseModel):
    """审核拒绝请求"""
    user_id: int
    reason: str = Field(..., min_length=10, description="拒绝原因，至少 10 字")


class VerifyActionResponse(BaseModel):
    """审核操作响应"""
    success: bool
    message: str
    user_id: int


# ==================== 审核接口 ====================

@router.get("/verify/pending", response_model=VerifyUserListResponse)
async def get_pending_verifications(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取待审核用户列表
    
    仅管理员可访问
    """
    # TODO: 添加管理员权限检查
    
    # 查询待审核用户（is_verified=False 且有房产信息）
    query = db.query(User).filter(
        User.is_verified == False,
        User.property_cert_number != None,
        User.property_cert_number != ""
    )
    
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return VerifyUserListResponse(
        total=total,
        users=[VerifyUserItem.from_orm(user) for user in users]
    )


@router.post("/verify/approve", response_model=VerifyActionResponse)
async def approve_verification(
    request: VerifyApproveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    审核通过
    
    1. 设置用户为已认证
    2. 记录认证时间
    3. 清除拒绝原因
    """
    # TODO: 添加管理员权限检查
    
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已通过认证"
        )
    
    # 更新用户状态
    user.is_verified = True
    user.verified_at = datetime.now()
    user.verification_reject_reason = None
    user.updated_at = datetime.now()
    
    db.commit()
    
    logger.info(f"用户认证已通过：user_id={request.user_id}, admin_id={current_user.id}")
    
    # TODO: 发送认证通过通知
    
    return VerifyActionResponse(
        success=True,
        message="认证已通过",
        user_id=request.user_id
    )


@router.post("/verify/reject", response_model=VerifyActionResponse)
async def reject_verification(
    request: VerifyRejectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    审核拒绝
    
    1. 保持未认证状态
    2. 记录拒绝原因
    3. 允许用户重新提交
    """
    # TODO: 添加管理员权限检查
    
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 更新拒绝原因
    user.verification_reject_reason = request.reason
    user.updated_at = datetime.now()
    
    db.commit()
    
    logger.info(f"用户认证被拒绝：user_id={request.user_id}, reason={request.reason}")
    
    # TODO: 发送认证拒绝通知
    
    return VerifyActionResponse(
        success=True,
        message=f"认证已拒绝：{request.reason}",
        user_id=request.user_id
    )


@router.get("/verify/{user_id}")
async def get_user_verification(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户认证详情
    """
    # TODO: 添加管理员权限检查
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return {
        "user_id": user.id,
        "openid": user.openid,
        "nickname": user.nickname,
        "phone": user.phone,
        "is_verified": user.is_verified,
        "verified_at": user.verified_at.isoformat() if user.verified_at else None,
        "verification_reject_reason": user.verification_reject_reason,
        "property_owner": user.property_owner,
        "property_cert_number": user.property_cert_number,
        "property_address": user.property_address,
        "property_area": user.property_area,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None
    }
