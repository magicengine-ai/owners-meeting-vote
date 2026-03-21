"""
应用配置
支持本地开发和云托管环境
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "业主大会投票小程序"
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # 服务端口（微信云托管使用 8080，本地使用 8000）
    PORT: int = int(os.getenv("PORT", "8080"))
    WEB_CONCURRENCY: int = int(os.getenv("WEB_CONCURRENCY", "2"))
    
    # 数据库配置
    # 云托管环境变量：TENCENTCLOUD_MYSQL_HOST, TENCENTCLOUD_MYSQL_PORT, etc.
    DB_HOST: str = os.getenv("DB_HOST", os.getenv("TENCENTCLOUD_MYSQL_HOST", "localhost"))
    DB_PORT: str = os.getenv("DB_PORT", os.getenv("TENCENTCLOUD_MYSQL_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", os.getenv("TENCENTCLOUD_MYSQL_DATABASE", "vote_db"))
    DB_USER: str = os.getenv("DB_USER", os.getenv("TENCENTCLOUD_MYSQL_USERNAME", "postgres"))
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", os.getenv("TENCENTCLOUD_MYSQL_PASSWORD", "postgres"))
    
    # Redis 配置
    # 云托管环境变量：TENCENTCLOUD_REDIS_HOST, TENCENTCLOUD_REDIS_PORT, etc.
    REDIS_HOST: str = os.getenv("REDIS_HOST", os.getenv("TENCENTCLOUD_REDIS_HOST", "localhost"))
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", os.getenv("TENCENTCLOUD_REDIS_PORT", "6379")))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", os.getenv("TENCENTCLOUD_REDIS_PASSWORD", ""))
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
