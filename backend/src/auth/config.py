"""
认证模块配置
"""
from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    """认证配置"""
    
    # JWT 配置
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # 微信配置
    WECHAT_APP_ID: str = ""
    WECHAT_APP_SECRET: str = ""
    
    # OCR 配置
    OCR_APP_ID: str = ""
    OCR_API_KEY: str = ""
    OCR_SECRET_KEY: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = AuthSettings()
