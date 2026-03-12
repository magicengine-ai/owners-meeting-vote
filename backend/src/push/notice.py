"""
消息通知推送模块
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import logging

from ..db import get_db
from ..models import User, Notice
from ..auth.utils import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== 数据模型 ====================

class NoticeCreateRequest(BaseModel):
    """创建通知请求"""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=10, max_length=5000)
    notice_type: str = Field(default="general", description="通知类型：general/urgent/meeting")
    target_users: Optional[List[int]] = Field(None, description="目标用户 ID 列表，为空则发送给所有用户")


class NoticeItem(BaseModel):
    """通知项"""
    id: int
    title: str
    content: str
    notice_type: str
    is_published: bool
    published_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class NoticeListResponse(BaseModel):
    """通知列表响应"""
    total: int
    notices: List[NoticeItem]


class NoticeDetailResponse(BaseModel):
    """通知详情响应"""
    id: int
    title: str
    content: str
    notice_type: str
    is_published: bool
    published_at: Optional[datetime]
    created_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]


class UserNoticeItem(BaseModel):
    """用户通知项"""
    id: int
    title: str
    notice_type: str
    is_read: bool = False
    created_at: datetime


class UserNoticeListResponse(BaseModel):
    """用户通知列表响应"""
    total: int
    unread_count: int
    notices: List[UserNoticeItem]


# ==================== 通知管理接口（管理员） ====================

@router.post("/notices", response_model=NoticeDetailResponse)
async def create_notice(
    request: NoticeCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建通知
    
    仅管理员可访问
    """
    # TODO: 添加管理员权限检查
    
    notice = Notice(
        title=request.title,
        content=request.content,
        notice_type=request.notice_type,
        is_published=False,
        created_by=current_user.id,
        created_at=datetime.now()
    )
    
    db.add(notice)
    db.commit()
    db.refresh(notice)
    
    logger.info(f"创建通知：notice_id={notice.id}, title={request.title}")
    
    return NoticeDetailResponse(
        id=notice.id,
        title=notice.title,
        content=notice.content,
        notice_type=notice.notice_type,
        is_published=notice.is_published,
        published_at=notice.published_at,
        created_by=notice.created_by,
        created_at=notice.created_at,
        updated_at=notice.updated_at
    )


@router.post("/notices/{notice_id}/publish")
async def publish_notice(
    notice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    发布通知
    
    仅管理员可访问
    """
    # TODO: 添加管理员权限检查
    
    notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在"
        )
    
    notice.is_published = True
    notice.published_at = datetime.now()
    notice.updated_at = datetime.now()
    
    db.commit()
    
    logger.info(f"发布通知：notice_id={notice_id}")
    
    # TODO: 发送推送通知给所有用户
    
    return {
        "success": True,
        "message": "通知已发布",
        "notice_id": notice_id
    }


@router.get("/notices", response_model=NoticeListResponse)
async def get_notices(
    page: int = 1,
    page_size: int = 20,
    notice_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取通知列表（管理员）
    """
    # TODO: 添加管理员权限检查
    
    query = db.query(Notice)
    
    if notice_type:
        query = query.filter(Notice.notice_type == notice_type)
    
    total = query.count()
    notices = query.order_by(Notice.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    return NoticeListResponse(
        total=total,
        notices=[NoticeItem.from_orm(notice) for notice in notices]
    )


# ==================== 用户通知接口 ====================

@router.get("/user/notices", response_model=UserNoticeListResponse)
async def get_user_notices(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户通知列表
    """
    # 查询已发布的通知
    query = db.query(Notice).filter(
        Notice.is_published == True
    )
    
    total = query.count()
    notices = query.order_by(Notice.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    # TODO: 实现未读状态跟踪
    unread_count = 0  # 临时值
    
    return UserNoticeListResponse(
        total=total,
        unread_count=unread_count,
        notices=[UserNoticeItem(
            id=notice.id,
            title=notice.title,
            notice_type=notice.notice_type,
            is_read=False,
            created_at=notice.created_at
        ) for notice in notices]
    )


@router.get("/user/notices/{notice_id}")
async def get_user_notice_detail(
    notice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取通知详情
    """
    notice = db.query(Notice).filter(
        Notice.id == notice_id,
        Notice.is_published == True
    ).first()
    
    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通知不存在或未发布"
        )
    
    return {
        "id": notice.id,
        "title": notice.title,
        "content": notice.content,
        "notice_type": notice.notice_type,
        "published_at": notice.published_at.isoformat() if notice.published_at else None,
        "created_at": notice.created_at.isoformat()
    }


# ==================== 认证结果通知 ====================

async def send_verify_approved_notice(
    user_id: int,
    db: Session
):
    """
    发送认证通过通知
    
    内部函数，在审核通过时调用
    """
    notice = Notice(
        title="认证通过通知",
        content="恭喜您，您的业主身份认证已通过审核！现在您可以参与小区投票和会议了。",
        notice_type="general",
        is_published=True,
        published_at=datetime.now(),
        created_at=datetime.now()
    )
    
    # TODO: 实现针对特定用户的通知
    # 目前创建全局通知
    
    db.add(notice)
    db.commit()
    
    logger.info(f"发送认证通过通知：user_id={user_id}")


async def send_verify_rejected_notice(
    user_id: int,
    reason: str,
    db: Session
):
    """
    发送认证拒绝通知
    
    内部函数，在审核拒绝时调用
    """
    notice = Notice(
        title="认证审核通知",
        content=f"很抱歉，您的业主身份认证未通过审核。原因：{reason}。请修改后重新提交。",
        notice_type="urgent",
        is_published=True,
        published_at=datetime.now(),
        created_at=datetime.now()
    )
    
    # TODO: 实现针对特定用户的通知
    
    db.add(notice)
    db.commit()
    
    logger.info(f"发送认证拒绝通知：user_id={user_id}, reason={reason}")
