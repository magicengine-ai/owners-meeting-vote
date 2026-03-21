"""
审核历史记录模块
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import logging

from ..db import get_db
from ..models import User
from .permissions import get_current_admin_user

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== 数据模型 ====================

class VerifyHistoryItem(BaseModel):
    """审核历史项"""
    id: int
    user_id: int
    user_nickname: Optional[str]
    user_phone: Optional[str]
    action: str  # approve/reject
    reason: Optional[str]
    admin_id: int
    admin_nickname: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class VerifyHistoryListResponse(BaseModel):
    """审核历史列表响应"""
    total: int
    history: List[VerifyHistoryItem]


# ==================== 审核历史接口 ====================

@router.get("/verify/history", response_model=VerifyHistoryListResponse)
async def get_verify_history(
    page: int = 1,
    page_size: int = 20,
    action: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取审核历史记录
    
    支持筛选：
    - action: 操作类型（approve/reject）
    - start_date: 开始日期（ISO 8601）
    - end_date: 结束日期（ISO 8601）
    """
    # TODO: 实现审核历史表查询
    # 目前返回空列表
    
    return VerifyHistoryListResponse(
        total=0,
        history=[]
    )


@router.get("/verify/stats")
async def get_verify_stats(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取审核统计数据
    """
    # TODO: 实现审核统计
    
    return {
        "total_pending": 0,
        "total_approved": 0,
        "total_rejected": 0,
        "today_approved": 0,
        "today_rejected": 0
    }
