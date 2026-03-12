"""
日志配置
"""
import sys
from loguru import logger
from pathlib import Path


def setup_logger(log_dir: str = "logs", level: str = "INFO"):
    """
    配置日志系统
    
    Args:
        log_dir: 日志目录
        level: 日志级别
    """
    # 移除默认的 handler
    logger.remove()
    
    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # 控制台输出
    logger.add(
        sys.stdout,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # 文件输出（所有日志）
    logger.add(
        log_path / "app.log",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )
    
    # 错误日志
    logger.add(
        log_path / "error.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    logger.info("日志系统初始化完成")
    
    return logger
