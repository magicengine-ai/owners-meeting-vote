"""
业主大会投票小程序 - 主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

# 配置日志
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>")
logger.add("logs/app.log", rotation="10 MB", retention="7 days", level="DEBUG")

app = FastAPI(
    title="业主大会投票小程序 API",
    description="业主大会投票系统后端服务",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}

# 导入路由
# from .routes import auth, vote, meeting, chain, push

# 注册路由
# app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
# app.include_router(vote.router, prefix="/api/vote", tags=["投票"])
# app.include_router(meeting.router, prefix="/api/meeting", tags=["会议"])
# app.include_router(chain.router, prefix="/api/chain", tags=["区块链"])
# app.include_router(push.router, prefix="/api/push", tags=["消息推送"])

@app.on_event("startup")
async def startup_event():
    logger.info("应用启动中...")
    # TODO: 初始化数据库连接
    # TODO: 初始化 Redis 连接
    # TODO: 初始化第三方服务（OCR、区块链等）
    logger.info("应用启动完成")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("应用关闭中...")
    # TODO: 关闭数据库连接
    # TODO: 关闭 Redis 连接
    logger.info("应用已关闭")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
