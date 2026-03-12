"""
测试配置文件
"""
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db import Base, get_db
from src.config import settings


# 测试数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """创建测试客户端"""
    from fastapi.testclient import TestClient
    from src.main import app
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user():
    """创建测试用户"""
    return {
        "openid": "test_openid_123",
        "nickname": "测试用户",
        "phone": "13800138000",
        "is_verified": True
    }


@pytest.fixture
def admin_user():
    """创建管理员用户"""
    return {
        "openid": "admin_openid_123",
        "nickname": "管理员",
        "is_admin": True
    }
