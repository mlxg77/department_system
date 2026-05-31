"""
通用 API 响应结构（Pydantic Schema）。

所有接口统一返回格式：
{
  "code": 0,           // 0 表示成功，非 0 表示错误
  "message": "success",
  "data": { ... }      // 实际业务数据
}
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """统一 API 响应包装器。"""
    code: int = 0
    message: str = "success"
    data: T | None = None


class PageData(BaseModel, Generic[T]):
    """分页数据结构，用于列表接口的 data 字段。"""
    items: list[T]      # 当前页的数据列表
    total: int          # 总记录数
    page: int           # 当前页码
    page_size: int      # 每页条数


class PageParams(BaseModel):
    """分页查询参数。"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
