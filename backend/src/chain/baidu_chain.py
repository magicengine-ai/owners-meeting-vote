"""
区块链存证模块 - 百度超级链
"""
import httpx
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import hashlib
import json

from ..config import settings

logger = logging.getLogger(__name__)


class BaiduChainClient:
    """百度超级链客户端"""
    
    def __init__(self):
        self.endpoint = settings.CHAIN_ENDPOINT or "https://xchain.baidu.com"
        self.chain_id = settings.CHAIN_CHAIN_ID or "test-chain"
        self.app_id = ""  # 从配置获取
        self.app_key = ""  # 从配置获取
    
    async def put_record(
        self,
        record_type: str,
        record_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        存证上链
        
        Args:
            record_type: 记录类型（vote/proxy等）
            record_data: 记录数据
            
        Returns:
            交易哈希，失败返回 None
        """
        try:
            # 生成数据哈希
            data_hash = self._generate_hash(record_data)
            
            # 构建存证数据
            chain_data = {
                "record_type": record_type,
                "data_hash": data_hash,
                "original_data": record_data,
                "timestamp": datetime.now().isoformat()
            }
            
            # 开发环境：模拟上链
            if not self.app_id or not self.app_key:
                logger.info(f"模拟上链：type={record_type}, hash={data_hash}")
                return f"mock_tx_{data_hash[:16]}"
            
            # 生产环境：调用百度超级链 API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.endpoint}/api/v1/record/put",
                    json={
                        "chain_id": self.chain_id,
                        "app_id": self.app_id,
                        "app_key": self.app_key,
                        "record": chain_data
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                if result.get("status") == "success":
                    tx_hash = result.get("tx_hash")
                    logger.info(f"上链成功：tx_hash={tx_hash}")
                    return tx_hash
                else:
                    logger.error(f"上链失败：{result.get('message', 'Unknown error')}")
                    return None
                    
        except Exception as e:
            logger.error(f"上链异常：{str(e)}", exc_info=True)
            return None
    
    async def query_record(
        self,
        tx_hash: str
    ) -> Optional[Dict[str, Any]]:
        """
        查询链上存证
        
        Args:
            tx_hash: 交易哈希
            
        Returns:
            存证数据，失败返回 None
        """
        try:
            # 开发环境：模拟查询
            if not self.app_id or not self.app_key:
                logger.info(f"模拟查询：tx_hash={tx_hash}")
                return {
                    "tx_hash": tx_hash,
                    "status": "confirmed",
                    "block_number": 12345,
                    "timestamp": datetime.now().isoformat()
                }
            
            # 生产环境：调用百度超级链 API
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.endpoint}/api/v1/record/query",
                    params={
                        "chain_id": self.chain_id,
                        "tx_hash": tx_hash
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                result = response.json()
                
                if result.get("status") == "success":
                    return result.get("record")
                else:
                    logger.error(f"查询失败：{result.get('message', 'Unknown error')}")
                    return None
                    
        except Exception as e:
            logger.error(f"查询异常：{str(e)}", exc_info=True)
            return None
    
    def _generate_hash(self, data: Dict[str, Any]) -> str:
        """生成数据哈希"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()


# 全局实例
chain_client = BaiduChainClient()


# ==================== 便捷函数 ====================

async def put_vote_record(
    vote_id: int,
    user_id: int,
    options: list,
    timestamp: str
) -> Optional[str]:
    """
    投票记录上链
    
    Args:
        vote_id: 投票 ID
        user_id: 用户 ID
        options: 投票选项
        timestamp: 时间戳
        
    Returns:
        交易哈希
    """
    record_data = {
        "vote_id": vote_id,
        "user_id": user_id,
        "options": options,
        "timestamp": timestamp
    }
    
    return await chain_client.put_record("vote", record_data)


async def put_proxy_record(
    delegator_id: int,
    proxy_id: int,
    vote_id: int,
    timestamp: str
) -> Optional[str]:
    """
    委托记录上链
    
    Args:
        delegator_id: 委托人 ID
        proxy_id: 受托人 ID
        vote_id: 投票 ID
        timestamp: 时间戳
        
    Returns:
        交易哈希
    """
    record_data = {
        "delegator_id": delegator_id,
        "proxy_id": proxy_id,
        "vote_id": vote_id,
        "timestamp": timestamp
    }
    
    return await chain_client.put_record("proxy", record_data)


async def query_chain_record(tx_hash: str) -> Optional[Dict[str, Any]]:
    """
    查询链上存证
    
    Args:
        tx_hash: 交易哈希
        
    Returns:
        存证数据
    """
    return await chain_client.query_record(tx_hash)
