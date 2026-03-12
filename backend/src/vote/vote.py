"""
投票模块
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import logging

from ..db import get_db
from ..config import settings
from ..models import Vote, VoteRecord, User
from ..auth.utils import get_current_user
from ..admin.permissions import get_current_admin_user
from sqlalchemy import func
import hashlib
import json

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== 数据模型 ====================

class VoteCreateRequest(BaseModel):
    """创建投票请求"""
    title: str = Field(..., description="投票标题")
    description: str = Field(..., description="投票描述")
    start_time: datetime
    end_time: datetime
    options: List[str] = Field(..., description="投票选项列表")
    vote_type: str = Field(default="single", description="投票类型：single/multiple")
    min_votes: int = Field(default=1, description="最少投票数")
    max_votes: int = Field(default=1, description="最多投票数")
    pass_threshold: float = Field(default=0.5, description="通过阈值（0-1）")


class VoteCreateResponse(BaseModel):
    """创建投票响应"""
    vote_id: str
    title: str
    status: str = "active"


class VoteSubmitRequest(BaseModel):
    """提交投票请求"""
    vote_id: str
    options: List[str] = Field(..., description="选择的选项")
    proxy_openid: Optional[str] = Field(None, description="受托人 openid（委托投票时）")


class VoteSubmitResponse(BaseModel):
    """提交投票响应"""
    success: bool
    vote_record_id: str
    timestamp: datetime


class VoteResult(BaseModel):
    """投票结果"""
    option: str
    count: int
    percentage: float


class VoteResultResponse(BaseModel):
    """投票结果响应"""
    vote_id: str
    title: str
    total_votes: int
    results: List[VoteResult]
    status: str
    passed: Optional[bool]


# ==================== 投票管理 ====================

@router.post("/create", response_model=VoteCreateResponse)
async def create_vote(
    request: VoteCreateRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    创建投票
    
    只有管理员/业委会成员可以创建投票
    """
    # 验证时间
    if request.start_time >= request.end_time:
        raise HTTPException(status_code=400, detail="开始时间必须早于结束时间")
    
    # 验证选项数量
    if len(request.options) < 2:
        raise HTTPException(status_code=400, detail="投票选项至少需要 2 个")
    
    # 创建投票记录
    vote = Vote(
        title=request.title,
        description=request.description,
        vote_type=request.vote_type,
        options=request.options,
        min_votes=request.min_votes,
        max_votes=request.max_votes,
        pass_threshold=request.pass_threshold,
        start_time=request.start_time,
        end_time=request.end_time,
        status="active",
        created_by=current_user.id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    db.add(vote)
    db.commit()
    db.refresh(vote)
    
    logger.info(f"创建投票：vote_id={vote.id}, title={request.title}, admin_id={current_user.id}")
    
    return VoteCreateResponse(
        vote_id=str(vote.id),
        title=vote.title,
        status=vote.status
    )


@router.get("/list")
async def list_votes(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    投票列表
    
    支持按状态筛选：active/completed/cancelled
    """
    query = db.query(Vote)
    
    if status:
        query = query.filter(Vote.status == status)
    
    total = query.count()
    votes = query.order_by(Vote.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    
    # 统计每个投票的投票数
    vote_list = []
    for vote in votes:
        vote_count = db.query(func.count(VoteRecord.id)).filter(
            VoteRecord.vote_id == vote.id
        ).scalar()
        
        vote_list.append({
            "vote_id": str(vote.id),
            "title": vote.title,
            "description": vote.description,
            "start_time": vote.start_time.isoformat(),
            "end_time": vote.end_time.isoformat(),
            "status": vote.status,
            "total_votes": vote_count,
            "vote_type": vote.vote_type
        })
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "votes": vote_list
    }


@router.get("/detail/{vote_id}")
async def get_vote_detail(vote_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    投票详情
    """
    vote = db.query(Vote).filter(Vote.id == vote_id).first()
    if not vote:
        raise HTTPException(status_code=404, detail="投票不存在")
    
    # 统计投票数
    vote_count = db.query(func.count(VoteRecord.id)).filter(
        VoteRecord.vote_id == vote_id
    ).scalar()
    
    # 检查当前用户是否已投票
    has_voted = False
    if current_user:
        user_vote = db.query(VoteRecord).filter(
            VoteRecord.vote_id == vote_id,
            VoteRecord.user_id == current_user.id
        ).first()
        has_voted = user_vote is not None
    
    return {
        "vote_id": str(vote.id),
        "title": vote.title,
        "description": vote.description,
        "options": vote.options,
        "vote_type": vote.vote_type,
        "min_votes": vote.min_votes,
        "max_votes": vote.max_votes,
        "pass_threshold": vote.pass_threshold,
        "start_time": vote.start_time.isoformat(),
        "end_time": vote.end_time.isoformat(),
        "status": vote.status,
        "total_votes": vote_count,
        "created_by": vote.created_by,
        "has_voted": has_voted
    }


@router.post("/submit", response_model=VoteSubmitResponse)
async def submit_vote(
    request: VoteSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    提交投票
    
    1. 验证投票资格（必须是认证业主）
    2. 验证是否已投票
    3. 验证投票时间
    4. 保存投票记录
    5. 区块链存证
    """
    # 1. 验证投票资格
    if not current_user.is_verified:
        raise HTTPException(status_code=403, detail="只有认证业主才能投票")
    
    # 2. 查询投票
    vote_id = int(request.vote_id)
    vote = db.query(Vote).filter(Vote.id == vote_id).first()
    if not vote:
        raise HTTPException(status_code=404, detail="投票不存在")
    
    # 3. 验证投票时间
    now = datetime.now()
    if now < vote.start_time:
        raise HTTPException(status_code=400, detail="投票尚未开始")
    if now > vote.end_time:
        raise HTTPException(status_code=400, detail="投票已结束")
    
    # 4. 检查是否重复投票
    existing_vote = db.query(VoteRecord).filter(
        VoteRecord.vote_id == vote_id,
        VoteRecord.user_id == current_user.id
    ).first()
    if existing_vote:
        raise HTTPException(status_code=400, detail="您已经投过票了")
    
    # 5. 验证投票选项
    if len(request.options) < vote.min_votes:
        raise HTTPException(status_code=400, detail=f"最少选择{vote.min_votes}个选项")
    if len(request.options) > vote.max_votes:
        raise HTTPException(status_code=400, detail=f"最多选择{vote.max_votes}个选项")
    
    # 6. 保存投票记录
    vote_record = VoteRecord(
        vote_id=vote_id,
        user_id=current_user.id,
        options=request.options,
        is_proxy=request.proxy_openid is not None,
        created_at=now
    )
    
    db.add(vote_record)
    db.commit()
    db.refresh(vote_record)
    
    # 7. 区块链存证（简化版）
    chain_hash = generate_chain_hash(vote_record)
    vote_record.chain_tx_hash = chain_hash
    db.commit()
    
    logger.info(f"投票成功：vote_id={vote_id}, user_id={current_user.id}, record_id={vote_record.id}")
    
    return VoteSubmitResponse(
        success=True,
        vote_record_id=str(vote_record.id),
        timestamp=now
    )


def generate_chain_hash(vote_record: VoteRecord) -> str:
    """生成区块链存证哈希"""
    data = {
        "vote_id": vote_record.vote_id,
        "user_id": vote_record.user_id,
        "options": vote_record.options,
        "timestamp": vote_record.created_at.isoformat()
    }
    data_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data_str.encode()).hexdigest()


@router.get("/result/{vote_id}", response_model=VoteResultResponse)
async def get_vote_result(vote_id: int, db: Session = Depends(get_db)):
    """
    投票结果
    
    实时统计投票结果
    """
    vote = db.query(Vote).filter(Vote.id == vote_id).first()
    if not vote:
        raise HTTPException(status_code=404, detail="投票不存在")
    
    # 统计总票数
    total_votes = db.query(func.count(VoteRecord.id)).filter(
        VoteRecord.vote_id == vote_id
    ).scalar() or 0
    
    # 统计各选项票数
    results = []
    for option in vote.options:
        option_count = db.query(func.count(VoteRecord.id)).filter(
            VoteRecord.vote_id == vote_id,
            VoteRecord.options.contains([option])
        ).scalar() or 0
        
        percentage = option_count / total_votes if total_votes > 0 else 0
        
        results.append(VoteResult(
            option=option,
            count=option_count,
            percentage=round(percentage, 3)
        ))
    
    # 判断是否通过（简单规则：赞成票超过阈值）
    passed = None
    if total_votes > 0 and "赞成" in vote.options:
        approve_count = next((r.count for r in results if r.option == "赞成"), 0)
        passed = approve_count / total_votes >= vote.pass_threshold
    
    return VoteResultResponse(
        vote_id=str(vote.id),
        title=vote.title,
        total_votes=total_votes,
        results=results,
        status=vote.status,
        passed=passed
    )


@router.post("/cancel/{vote_id}")
async def cancel_vote(vote_id: str, openid: str, db: Session = Depends(get_db)):
    """
    取消投票
    
    只有创建者/管理员可以取消投票
    """
    # TODO: 验证权限
    # TODO: 更新投票状态
    
    return {"success": True, "message": "投票已取消"}


# ==================== 委托投票 ====================

@router.post("/proxy/assign")
async def assign_proxy(
    proxy_openid: str,
    vote_id: str,
    openid: str,
    db: Session = Depends(get_db)
):
    """
    委托投票
    
    业主可以委托其他业主代为投票
    """
    # TODO: 验证受托人资格
    # TODO: 创建委托关系
    # TODO: 区块链存证
    
    logger.info(f"委托投票：openid={openid}, proxy={proxy_openid}")
    
    return {"success": True, "message": "委托成功"}


@router.post("/proxy/revoke")
async def revoke_proxy(
    vote_id: str,
    openid: str,
    db: Session = Depends(get_db)
):
    """
    撤销委托
    """
    # TODO: 撤销委托关系
    
    return {"success": True, "message": "委托已撤销"}
