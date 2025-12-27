from typing import Generic, TypeVar, Optional, Any

from pydantic import BaseModel

from app.schemas.base import CamelModel

T = TypeVar('T')


class ResponseModel(CamelModel, Generic[T]):
    """通用响应模型"""
    success: bool = True
    message: str = ""
    data: Optional[T] = None
    code: int = 200


class OperationResponse(CamelModel):
    """操作响应模型"""
    success: bool = True
    message: str = ""
    operation: str = ""
    details: Optional[Any] = None
    code: int = 200