"""
数据库模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    openid = Column(String(64), unique=True, index=True, nullable=False)
    unionid = Column(String(64), unique=True, index=True)
    nickname = Column(String(64))
    avatar_url = Column(String(255))
    phone = Column(String(20))
    
    # 认证状态
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime)
    verification_reject_reason = Column(String(255))
    
    # 房产信息
    property_cert_number = Column(String(64))  # 房产证号
    property_owner = Column(String(64))  # 产权人
    property_address = Column(String(255))  # 房产地址
    property_area = Column(Float)  # 面积
    
    # 楼栋信息
    building_id = Column(Integer, ForeignKey("buildings.id"))
    unit_id = Column(Integer, ForeignKey("units.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    
    # 时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    building = relationship("Building")
    unit = relationship("Unit")
    room = relationship("Room")
    votes = relationship("VoteRecord", back_populates="user")


class Building(Base):
    """楼栋表"""
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), nullable=False)  # 楼栋名称
    total_units = Column(Integer)  # 总单元数
    total_floors = Column(Integer)  # 总楼层
    total_rooms = Column(Integer)  # 总房间数
    
    units = relationship("Unit", back_populates="building")


class Unit(Base):
    """单元表"""
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)
    name = Column(String(64), nullable=False)  # 单元名称
    
    building = relationship("Building", back_populates="units")
    rooms = relationship("Room", back_populates="unit")


class Room(Base):
    """房间表"""
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    name = Column(String(64), nullable=False)  # 房间号
    area = Column(Float)  # 建筑面积
    
    unit = relationship("Unit", back_populates="rooms")


class Vote(Base):
    """投票表"""
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # 投票配置
    vote_type = Column(String(20), default="single")  # single/multiple
    options = Column(JSON, nullable=False)  # 选项列表
    min_votes = Column(Integer, default=1)
    max_votes = Column(Integer, default=1)
    pass_threshold = Column(Float, default=0.5)  # 通过阈值
    
    # 时间
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    
    # 状态
    status = Column(String(20), default="active")  # active/completed/cancelled
    result = Column(JSON)  # 投票结果
    
    # 创建者
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # 时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    records = relationship("VoteRecord", back_populates="vote")


class VoteRecord(Base):
    """投票记录表"""
    __tablename__ = "vote_records"

    id = Column(Integer, primary_key=True, index=True)
    vote_id = Column(Integer, ForeignKey("votes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 投票内容
    options = Column(JSON, nullable=False)  # 选择的选项
    
    # 是否委托
    is_proxy = Column(Boolean, default=False)
    proxy_user_id = Column(Integer, ForeignKey("users.id"))  # 受托人
    
    # 区块链存证
    chain_tx_hash = Column(String(128))  # 交易哈希
    chain_block_number = Column(Integer)  # 区块号
    chain_timestamp = Column(DateTime)  # 存证时间
    
    # 时间
    created_at = Column(DateTime, default=datetime.now, unique=True)

    vote = relationship("Vote", back_populates="records")
    user = relationship("User", back_populates="votes")


class Meeting(Base):
    """会议表"""
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # 时间地点
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String(255))
    
    # 状态
    status = Column(String(20), default="upcoming")  # upcoming/ongoing/completed/cancelled
    
    # 内容
    agenda = Column(JSON)  # 议程
    materials = Column(JSON)  # 会议材料
    
    # 创建者
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # 时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    attendees = relationship("MeetingAttendee", back_populates="meeting")


class MeetingAttendee(Base):
    """会议签到表"""
    __tablename__ = "meeting_attendees"

    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 签到
    check_in_time = Column(DateTime)
    check_in_method = Column(String(20))  # qr_code/face/manual
    
    # 签名
    signature_image = Column(String(255))  # 签名图片 URL
    
    # 时间
    created_at = Column(DateTime, default=datetime.now)

    meeting = relationship("Meeting", back_populates="attendees")


class ChainRecord(Base):
    """区块链存证记录表"""
    __tablename__ = "chain_records"

    id = Column(Integer, primary_key=True, index=True)
    record_type = Column(String(20), nullable=False)  # vote/meeting
    record_id = Column(Integer, nullable=False)  # 对应记录 ID
    
    # 区块链信息
    tx_hash = Column(String(128), unique=True)
    block_number = Column(Integer)
    timestamp = Column(DateTime)
    
    # 数据哈希
    data_hash = Column(String(64), index=True)
    
    # 时间
    created_at = Column(DateTime, default=datetime.now)


class Notice(Base):
    """公告表"""
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    
    # 类型
    notice_type = Column(String(20), default="general")  # general/urgent/meeting
    
    # 状态
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime)
    
    # 创建者
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # 时间
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
