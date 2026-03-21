"""
数据库配置
支持 PostgreSQL（本地）和 MySQL（云托管）
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import os

# 检测数据库类型（云托管使用 MySQL，本地开发使用 PostgreSQL）
DB_TYPE = os.getenv("DB_TYPE", "auto").lower()

if DB_TYPE == "auto":
    # 自动检测：如果有 TENCENTCLOUD_MYSQL_HOST 则是云托管环境
    if os.getenv("TENCENTCLOUD_MYSQL_HOST"):
        DB_TYPE = "mysql"
    else:
        DB_TYPE = "postgresql"

# 构建数据库 URL
if DB_TYPE == "mysql":
    # MySQL（云托管）
    SQLALCHEMY_DATABASE_URL = (
        f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        f"?charset=utf8mb4"
    )
    engine_kwargs = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 3600,
        "pool_pre_ping": True  # 连接池健康检查
    }
else:
    # PostgreSQL（本地开发）
    SQLALCHEMY_DATABASE_URL = (
        f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
    engine_kwargs = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 3600,
        "pool_pre_ping": True
    }

# 创建引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 依赖注入：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
