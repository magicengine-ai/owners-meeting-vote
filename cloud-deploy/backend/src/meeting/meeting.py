"""
会议管理模块
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import logging

from ..db import get_db
from ..models import Meeting, MeetingAttendee, User
from ..auth.utils import get_current_user
from ..admin.permissions import get_current_admin_user
from sqlalchemy import func

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== 数据模型 ====================

class MeetingCreateRequest(BaseModel):
    """创建会议请求"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    start_time: datetime
    end_time: datetime
    location: Optional[str] = Field(None, max_length=255)
    agenda: Optional[List[str]] = Field(None, description="议程列表")
    materials: Optional[List[str]] = Field(None, description="会议材料 URL 列表")


class MeetingCreateResponse(BaseModel):
    """创建会议响应"""
    meeting_id: int
    title: str
    status: str = "upcoming"


class MeetingUpdateRequest(BaseModel):
    """更新会议请求"""
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    agenda: Optional[List[str]] = None
    materials: Optional[List[str]] = None
    status: Optional[str] = None


class MeetingItem(BaseModel):
    """会议项"""
    meeting_id: int
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    location: Optional[str]
    status: str
    total_attendees: int = 0
    
    class Config:
        from_attributes = True


class MeetingListResponse(BaseModel):
    """会议列表响应"""
    total: int
    meetings: List[MeetingItem]


class MeetingDetailResponse(BaseModel):
    """会议详情响应"""
    meeting_id: int
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    location: Optional[str]
    status: str
    agenda: Optional[List[str]]
    materials: Optional[List[str]]
    created_by: int
    total_attendees: int
    checked_in_count: int
    has_signed_up: bool = False


class MeetingSignUpRequest(BaseModel):
    """会议报名请求"""
    meeting_id: int


class MeetingSignUpResponse(BaseModel):
    """会议报名响应"""
    success: bool
    message: str
    attendee_id: int


class MeetingCheckInRequest(BaseModel):
    """会议签到请求"""
    meeting_id: int
    check_in_method: str = Field(default="qr_code", description="签到方式：qr_code/face/manual")


class MeetingCheckInResponse(BaseModel):
    """会议签到响应"""
    success: bool
    message: str
    check_in_time: datetime


class MeetingStatsResponse(BaseModel):
    """会议统计响应"""
    total_attendees: int
    checked_in_count: int
    check_in_rate: float


# ==================== 会议管理 ====================

@router.post("/create", response_model=MeetingCreateResponse)
async def create_meeting(
    request: MeetingCreateRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    创建会议
    
    仅管理员可创建会议
    """
    # 验证时间
    if request.start_time >= request.end_time:
        raise HTTPException(status_code=400, detail="开始时间必须早于结束时间")
    
    # 创建会议
    meeting = Meeting(
        title=request.title,
        description=request.description,
        start_time=request.start_time,
        end_time=request.end_time,
        location=request.location,
        agenda=request.agenda if request.agenda else [],
        materials=request.materials if request.materials else [],
        status="upcoming",
        created_by=current_user.id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    
    logger.info(f"创建会议：meeting_id={meeting.id}, title={request.title}, admin_id={current_user.id}")
    
    return MeetingCreateResponse(
        meeting_id=meeting.id,
        title=meeting.title,
        status=meeting.status
    )


@router.get("/list", response_model=MeetingListResponse)
async def list_meetings(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    会议列表
    
    支持按状态筛选：upcoming/ongoing/completed/cancelled
    """
    query = db.query(Meeting)
    
    if status:
        query = query.filter(Meeting.status == status)
    
    total = query.count()
    meetings = query.order_by(Meeting.start_time.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    # 统计参会人数
    meeting_list = []
    for meeting in meetings:
        attendee_count = db.query(func.count(MeetingAttendee.id)).filter(
            MeetingAttendee.meeting_id == meeting.id
        ).scalar()
        
        meeting_list.append(MeetingItem(
            meeting_id=meeting.id,
            title=meeting.title,
            description=meeting.description,
            start_time=meeting.start_time,
            end_time=meeting.end_time,
            location=meeting.location,
            status=meeting.status,
            total_attendees=attendee_count
        ))
    
    return MeetingListResponse(
        total=total,
        meetings=meeting_list
    )


@router.get("/detail/{meeting_id}", response_model=MeetingDetailResponse)
async def get_meeting_detail(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    会议详情
    """
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    
    # 统计参会人数
    total_attendees = db.query(func.count(MeetingAttendee.id)).filter(
        MeetingAttendee.meeting_id == meeting_id
    ).scalar() or 0
    
    # 统计已签到人数
    checked_in_count = db.query(func.count(MeetingAttendee.id)).filter(
        MeetingAttendee.meeting_id == meeting_id,
        MeetingAttendee.check_in_time != None
    ).scalar() or 0
    
    # 检查当前用户是否已报名
    has_signed_up = False
    if current_user:
        attendee = db.query(MeetingAttendee).filter(
            MeetingAttendee.meeting_id == meeting_id,
            MeetingAttendee.user_id == current_user.id
        ).first()
        has_signed_up = attendee is not None
    
    return MeetingDetailResponse(
        meeting_id=meeting.id,
        title=meeting.title,
        description=meeting.description,
        start_time=meeting.start_time,
        end_time=meeting.end_time,
        location=meeting.location,
        status=meeting.status,
        agenda=meeting.agenda,
        materials=meeting.materials,
        created_by=meeting.created_by,
        total_attendees=total_attendees,
        checked_in_count=checked_in_count,
        has_signed_up=has_signed_up
    )


@router.post("/update/{meeting_id}")
async def update_meeting(
    meeting_id: int,
    request: MeetingUpdateRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    更新会议
    
    仅管理员可更新会议
    """
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    
    # 更新字段
    if request.title is not None:
        meeting.title = request.title
    if request.description is not None:
        meeting.description = request.description
    if request.start_time is not None:
        meeting.start_time = request.start_time
    if request.end_time is not None:
        meeting.end_time = request.end_time
    if request.location is not None:
        meeting.location = request.location
    if request.agenda is not None:
        meeting.agenda = request.agenda
    if request.materials is not None:
        meeting.materials = request.materials
    if request.status is not None:
        meeting.status = request.status
    
    meeting.updated_at = datetime.now()
    
    db.commit()
    
    logger.info(f"更新会议：meeting_id={meeting_id}, admin_id={current_user.id}")
    
    return {
        "success": True,
        "message": "会议已更新",
        "meeting_id": meeting_id
    }


@router.post("/cancel/{meeting_id}")
async def cancel_meeting(
    meeting_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    取消会议
    
    仅管理员可取消会议
    """
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    
    meeting.status = "cancelled"
    meeting.updated_at = datetime.now()
    
    db.commit()
    
    logger.info(f"取消会议：meeting_id={meeting_id}, admin_id={current_user.id}")
    
    # TODO: 发送取消通知给所有报名用户
    
    return {
        "success": True,
        "message": "会议已取消",
        "meeting_id": meeting_id
    }


# ==================== 会议报名 ====================

@router.post("/signup", response_model=MeetingSignUpResponse)
async def sign_up_meeting(
    request: MeetingSignUpRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    报名参加会议
    """
    # 查询会议
    meeting = db.query(Meeting).filter(Meeting.id == request.meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    
    if meeting.status == "cancelled":
        raise HTTPException(status_code=400, detail="会议已取消")
    
    # 检查是否已报名
    existing = db.query(MeetingAttendee).filter(
        MeetingAttendee.meeting_id == request.meeting_id,
        MeetingAttendee.user_id == current_user.id
    ).first()
    
    if existing:
        return MeetingSignUpResponse(
            success=True,
            message="您已报名此会议",
            attendee_id=existing.id
        )
    
    # 创建报名记录
    attendee = MeetingAttendee(
        meeting_id=request.meeting_id,
        user_id=current_user.id,
        created_at=datetime.now()
    )
    
    db.add(attendee)
    db.commit()
    db.refresh(attendee)
    
    logger.info(f"会议报名：meeting_id={request.meeting_id}, user_id={current_user.id}")
    
    return MeetingSignUpResponse(
        success=True,
        message="报名成功",
        attendee_id=attendee.id
    )


@router.post("/cancel-signup/{meeting_id}")
async def cancel_sign_up(
    meeting_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    取消报名
    """
    attendee = db.query(MeetingAttendee).filter(
        MeetingAttendee.meeting_id == meeting_id,
        MeetingAttendee.user_id == current_user.id
    ).first()
    
    if not attendee:
        raise HTTPException(status_code=404, detail="未找到报名记录")
    
    if attendee.check_in_time:
        raise HTTPException(status_code=400, detail="已签到，无法取消报名")
    
    db.delete(attendee)
    db.commit()
    
    logger.info(f"取消报名：meeting_id={meeting_id}, user_id={current_user.id}")
    
    return {
        "success": True,
        "message": "已取消报名",
        "meeting_id": meeting_id
    }


# ==================== 会议签到 ====================

@router.post("/checkin", response_model=MeetingCheckInResponse)
async def check_in_meeting(
    request: MeetingCheckInRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    会议签到
    
    支持多种签到方式：二维码、人脸、手动
    """
    # 查询会议
    meeting = db.query(Meeting).filter(Meeting.id == request.meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")
    
    # 查询报名记录
    attendee = db.query(MeetingAttendee).filter(
        MeetingAttendee.meeting_id == request.meeting_id,
        MeetingAttendee.user_id == current_user.id
    ).first()
    
    if not attendee:
        raise HTTPException(status_code=404, detail="请先报名参加会议")
    
    if attendee.check_in_time:
        raise HTTPException(status_code=400, detail="您已签到")
    
    # 更新签到状态
    attendee.check_in_time = datetime.now()
    attendee.check_in_method = request.check_in_method
    
    db.commit()
    
    logger.info(f"会议签到：meeting_id={request.meeting_id}, user_id={current_user.id}, method={request.check_in_method}")
    
    return MeetingCheckInResponse(
        success=True,
        message="签到成功",
        check_in_time=attendee.check_in_time
    )


@router.get("/stats/{meeting_id}", response_model=MeetingStatsResponse)
async def get_meeting_stats(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    会议统计
    
    仅管理员可查看
    """
    # 总报名人数
    total_attendees = db.query(func.count(MeetingAttendee.id)).filter(
        MeetingAttendee.meeting_id == meeting_id
    ).scalar() or 0
    
    # 已签到人数
    checked_in_count = db.query(func.count(MeetingAttendee.id)).filter(
        MeetingAttendee.meeting_id == meeting_id,
        MeetingAttendee.check_in_time != None
    ).scalar() or 0
    
    # 签到率
    check_in_rate = checked_in_count / total_attendees if total_attendees > 0 else 0
    
    return MeetingStatsResponse(
        total_attendees=total_attendees,
        checked_in_count=checked_in_count,
        check_in_rate=round(check_in_rate, 3)
    )


# ==================== 会议记录 ====================

@router.get("/attendees/{meeting_id}")
async def get_meeting_attendees(
    meeting_id: int,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取会议参会人员列表
    
    仅管理员可查看
    """
    query = db.query(MeetingAttendee).filter(
        MeetingAttendee.meeting_id == meeting_id
    )
    
    total = query.count()
    attendees = query.order_by(
        MeetingAttendee.created_at.desc()
    ).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    attendee_list = []
    for attendee in attendees:
        user = db.query(User).filter(User.id == attendee.user_id).first()
        attendee_list.append({
            "attendee_id": attendee.id,
            "user_id": user.id if user else None,
            "nickname": user.nickname if user else None,
            "phone": user.phone if user else None,
            "check_in_time": attendee.check_in_time.isoformat() if attendee.check_in_time else None,
            "check_in_method": attendee.check_in_method,
            "signed_up_at": attendee.created_at.isoformat()
        })
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "attendees": attendee_list
    }
