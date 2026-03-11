"""
应用配置
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "业主大会投票小程序"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "vote_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    
    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # JWT 配置
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 天
    
    # 微信配置
    WECHAT_APP_ID: str = ""
    WECHAT_APP_SECRET: str = ""
    
    # OCR 配置（百度 AI）
    OCR_APP_ID: str = ""
    OCR_API_KEY: str = ""
    OCR_SECRET_KEY: str = ""
    
    # 区块链配置
    CHAIN_ENDPOINT: str = ""
    CHAIN_CHAIN_ID: str = ""
    
    # 短信配置
    SMS_PROVIDER: str = "aliyun"  # aliyun / tencent
    SMS_ACCESS_KEY: str = ""
    SMS_SECRET_KEY: str = ""
    SMS_SIGN_NAME: str = "业主大会"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
