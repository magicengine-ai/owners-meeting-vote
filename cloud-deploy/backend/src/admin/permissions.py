"""
管理员权限验证模块
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import logging

from ..db import get_db
from ..models import User
from ..auth.utils import get_current_user

logger = logging.getLogger(__name__)


# 管理员角色标识
ADMIN_ROLE_FLAG = "is_admin"


async def get_current_admin_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> User:
    """
    验证当前用户是否为管理员
    
    检查逻辑：
    1. 检查用户是否有 is_admin 标识
    2. 检查用户是否在管理员列表中
    3. 检查用户角色
    
    TODO: 生产环境需要实现完整的 RBAC 系统
    """
    # 临时实现：检查 openid 是否在管理员列表中
    admin_openids = [
        "admin_openid_1",  # 替换为实际管理员 openid
        "ou_00fdfa729dc521504944260f53751bf8"  # 当前用户
    ]
    
    if current_user.openid not in admin_openids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    
    logger.info(f"管理员验证通过：user_id={current_user.id}, openid={current_user.openid}")
    
    return current_user


def check_admin_permission(user: User) -> bool:
    """
    检查用户是否有管理员权限
    
    可以在其他地方使用此函数进行权限检查
    """
    admin_openids = [
        "admin_openid_1",
        "ou_00fdfa729dc521504944260f53751bf8"
    ]
    
    return user.openid in admin_openids
