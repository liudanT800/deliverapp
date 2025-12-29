from datetime import timedelta
import os

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas import auth as auth_schema
from app.schemas import user as user_schema
from app.schemas.response import ResponseModel

router = APIRouter(prefix="/auth", tags=["auth"])

# 开发模式开关
DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "false").lower() == "true"


@router.post("/register", response_model=ResponseModel[user_schema.UserRead], status_code=201)
async def register_user(
    request: Request,
    payload: user_schema.UserCreate,
    session: AsyncSession = Depends(deps.get_db),
):
    try:
        result = await session.execute(select(User).where(User.email == payload.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="该邮箱已注册")

        db_user = User(
            email=payload.email,
            full_name=payload.full_name,
            phone=payload.phone,
            campus=payload.campus,
            hashed_password=get_password_hash(payload.password),
            credit_score=3.5,
        )
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        
        request_id = getattr(request.state, 'request_id', None)
        return ResponseModel(
            success=True,
            message="用户注册成功",
            data=db_user,
            request_id=request_id
        )
    except HTTPException:
        await session.rollback()
        raise
    except SQLAlchemyError as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"数据库操作失败: {str(e)}")
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"注册过程中发生未知错误: {str(e)}")


@router.post("/login", response_model=ResponseModel[auth_schema.Token])
async def login(
    request: Request,
    payload: auth_schema.LoginRequest,
    session: AsyncSession = Depends(deps.get_db),
):
    try:
        result = await session.execute(select(User).where(User.email == payload.email))
        user = result.scalar_one_or_none()
        
        # 如果用户不存在，创建一个测试用户（仅在开发模式下）
        if not user and DEVELOPMENT_MODE:
            # 创建测试用户
            db_user = User(
                email=payload.email,
                full_name="测试用户",
                phone="13800138000",
                campus="测试校区",
                hashed_password=get_password_hash(payload.password),
                credit_score=3.5,
            )
            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)
            user = db_user
        
        # 检查用户是否存在
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
        
        # 在开发模式下跳过密码验证
        if not DEVELOPMENT_MODE:
            if not verify_password(payload.password, user.hashed_password):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="邮箱或密码错误")

        if not user.is_active:
            raise HTTPException(status_code=400, detail="账号被停用")

        token = create_access_token(user.email, timedelta(minutes=60 * 24))
        request_id = getattr(request.state, 'request_id', None)
        return ResponseModel(
            success=True,
            message="登录成功",
            data=auth_schema.Token(access_token=token),
            request_id=request_id
        )
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"数据库操作失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登录过程中发生未知错误: {str(e)}")