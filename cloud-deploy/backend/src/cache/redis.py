"""
Redis 缓存配置
"""
import redis
import json
from typing import Any, Optional
from datetime import timedelta
import logging

from .config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis 缓存客户端"""
    
    def __init__(self):
        """初始化 Redis 连接"""
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        logger.info(f"Redis 连接初始化：{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在返回 None
        """
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis GET 失败 {key}: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            expire: 过期时间（秒）
            
        Returns:
            是否成功
        """
        try:
            serialized = json.dumps(value, ensure_ascii=False)
            if expire:
                return self.client.setex(key, expire, serialized)
            else:
                return self.client.set(key, serialized)
        except Exception as e:
            logger.error(f"Redis SET 失败 {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功
        """
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Redis DELETE 失败 {key}: {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        检查键是否存在
        
        Args:
            key: 缓存键
            
        Returns:
            是否存在
        """
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS 失败 {key}: {str(e)}")
            return False
    
    def expire(self, key: str, seconds: int) -> bool:
        """
        设置过期时间
        
        Args:
            key: 缓存键
            seconds: 过期时间（秒）
            
        Returns:
            是否成功
        """
        try:
            return self.client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis EXPIRE 失败 {key}: {str(e)}")
            return False
    
    def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """
        自增
        
        Args:
            key: 缓存键
            amount: 增量
            
        Returns:
            自增后的值
        """
        try:
            return self.client.incr(key, amount)
        except Exception as e:
            logger.error(f"Redis INCR 失败 {key}: {str(e)}")
            return None
    
    def ttl(self, key: str) -> int:
        """
        获取剩余过期时间
        
        Args:
            key: 缓存键
            
        Returns:
            剩余时间（秒），-1 表示永不过期，-2 表示不存在
        """
        try:
            return self.client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL 失败 {key}: {str(e)}")
            return -2
    
    def ping(self) -> bool:
        """
        检查 Redis 连接
        
        Returns:
            是否连接正常
        """
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Redis PING 失败：{str(e)}")
            return False


# 全局缓存实例
cache = RedisCache()


def get_cache() -> RedisCache:
    """获取缓存实例（依赖注入）"""
    return cache
