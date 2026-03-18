"""
用户模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    openid = Column(String(100), unique=True, index=True, nullable=False)
    nickname = Column(String(100))
    avatar_url = Column(String(500))
    phone = Column(String(20))
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    property_info = Column(String(500))  # 房产信息
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
