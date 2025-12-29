import asyncio
import uuid
from typing import Dict, Any

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.schemas.response import ResponseModel, ErrorResponse
from app.services.task_cleanup_service import start_cleanup_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 启动定时清理任务
    asyncio.create_task(start_cleanup_scheduler())
    yield

app = FastAPI(title=settings.project_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """为每个请求添加请求ID"""
    request_id = f"req-{uuid.uuid4()}"
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    error_response = ErrorResponse.from_http_exception(exc.status_code, exc.detail)
    error_response.request_id = getattr(request.state, 'request_id', None)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    error_response = ErrorResponse.from_validation_error(exc.errors)
    error_response.request_id = getattr(request.state, 'request_id', None)
    
    return JSONResponse(
        status_code=422,
        content=error_response.model_dump()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    import traceback
    error_detail = f"{str(exc)}\n{traceback.format_exc()}"
    print(f"服务器内部错误: {error_detail}")  # 打印到控制台
    
    error_response = ErrorResponse.from_general_exception()
    error_response.request_id = getattr(request.state, 'request_id', None)
    error_response.details = str(exc) if hasattr(exc, 'detail') else "Internal server error"
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )
    
    # 启动定时清理任务
    asyncio.create_task(start_cleanup_scheduler())


@app.get("/healthz")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_router, prefix=settings.api_prefix)