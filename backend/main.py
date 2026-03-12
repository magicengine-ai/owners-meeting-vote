"""
业主大会投票小程序 - 主应用入口
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger
import sys
from pathlib import Path

# 配置日志
from src.utils.logger import setup_logger
setup_logger(log_dir="logs", level="DEBUG")

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


# ==================== 全局异常处理 ====================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理"""
    logger.error(f"请求验证失败：{exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "validation_error",
            "detail": exc.errors(),
            "message": "请求参数验证失败"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    logger.error(f"未处理的异常：{str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_error",
            "detail": str(exc) if app.debug else "Internal server error",
            "message": "服务器内部错误"
        }
    )


# ==================== 中间件 ====================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """请求日志中间件"""
    logger.info(f"请求：{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"响应：{request.method} {request.url.path} - {response.status_code}")
    return response


# ==================== 路由 ====================

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}


# 根路径
@app.get("/")
async def root():
    return {
        "message": "欢迎使用业主大会投票小程序 API",
        "docs": "/docs",
        "health": "/health"
    }

# 导入路由
from src.auth.auth import router as auth_router
from src.vote.vote import router as vote_router
from src.admin import verify_router, history_router
from src.push.notice import router as notice_router

# 注册路由
app.include_router(auth_router, prefix="/api/auth", tags=["认证"])
app.include_router(vote_router, prefix="/api/vote", tags=["投票"])
app.include_router(verify_router, prefix="/api/admin", tags=["管理后台"])
app.include_router(history_router, prefix="/api/admin", tags=["管理后台"])
app.include_router(notice_router, prefix="/api", tags=["消息通知"])
# app.include_router(meeting.router, prefix="/api/meeting", tags=["会议"])
# app.include_router(chain.router, prefix="/api/chain", tags=["区块链"])

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
