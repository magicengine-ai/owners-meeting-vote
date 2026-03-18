"""
数据库依赖
提供数据库会话管理
"""
from sqlalchemy.orm import Session
from src.db import SessionLocal


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
