from typing import Generic, TypeVar, Optional, Any, Dict, List

from pydantic import BaseModel

from app.schemas.base import CamelModel

T = TypeVar('T')


class ResponseModel(CamelModel, Generic[T]):
    """通用响应模型"""
    success: bool = True
    message: str = ""
    data: Optional[T] = None
    code: int = 200
    request_id: Optional[str] = None  # 添加请求ID，便于追踪


class OperationResponse(CamelModel):
    """操作响应模型"""
    success: bool = True
    message: str = ""
    operation: str = ""
    details: Optional[Any] = None
    code: int = 200


class ValidationErrorDetail(CamelModel):
    """验证错误详情"""
    loc: List[str]
    msg: str
    type: str
    input: Optional[Any] = None


class ErrorResponse(CamelModel):
    """错误响应模型"""
    success: bool = False
    message: str = ""
    code: int = 400
    error_type: Optional[str] = None
    details: Optional[Any] = None
    request_id: Optional[str] = None

    @classmethod
    def from_validation_error(cls, errors: List[Dict[str, Any]]) -> 'ErrorResponse':
        """从验证错误创建错误响应"""
        return cls(
            message="请求参数验证失败",
            code=422,
            error_type="VALIDATION_ERROR",
            details=[ValidationErrorDetail(**error) for error in errors]
        )

    @classmethod
    def from_http_exception(cls, status_code: int, detail: str) -> 'ErrorResponse':
        """从HTTP异常创建错误响应"""
        error_type_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            422: "VALIDATION_ERROR",
            429: "TOO_MANY_REQUESTS",
            500: "INTERNAL_SERVER_ERROR",
        }
        
        return cls(
            message=detail,
            code=status_code,
            error_type=error_type_map.get(status_code, "UNKNOWN_ERROR"),
        )

    @classmethod
    def from_general_exception(cls, detail: str = "服务器内部错误") -> 'ErrorResponse':
        """从一般异常创建错误响应"""
        return cls(
            message=detail,
            code=500,
            error_type="INTERNAL_SERVER_ERROR",
        )