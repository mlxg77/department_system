"""
自定义异常与全局异常处理器。

所有业务错误统一抛出 BusinessError，
由 exception handler 转换为标准 JSON 响应格式：
{ "code": 40101, "message": "未登录", "data": null }
"""

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.common import ResponseModel


class BusinessError(Exception):
    """
    业务逻辑异常。

    参数：
    - code: 业务错误码（如 40101 表示未登录）
    - message: 给用户看的错误提示
    - http_status: HTTP 状态码（默认 400）
    """
    def __init__(self, code: int, message: str, http_status: int = 400):
        self.code = code
        self.message = message
        self.http_status = http_status
        super().__init__(message)


async def business_error_handler(_: Request, exc: BusinessError) -> JSONResponse:
    """处理 BusinessError，返回统一格式的 JSON 错误响应。"""
    return JSONResponse(
        status_code=exc.http_status,
        content=ResponseModel(code=exc.code, message=exc.message, data=None).model_dump(),
    )


async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    """
    处理请求参数校验失败（Pydantic 自动校验）。

    例如：用户名长度不够、邮箱格式不对等。
    """
    errors = exc.errors()
    message = errors[0]["msg"] if errors else "参数校验失败"
    return JSONResponse(
        status_code=422,
        content=ResponseModel(code=40001, message=message, data=errors).model_dump(),
    )
