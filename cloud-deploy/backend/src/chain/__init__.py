"""
区块链存证模块
"""
from .baidu_chain import (
    put_vote_record,
    put_proxy_record,
    query_chain_record,
    chain_client
)

__all__ = [
    "put_vote_record",
    "put_proxy_record",
    "query_chain_record",
    "chain_client"
]
