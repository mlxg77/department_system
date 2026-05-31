"""
认证相关请求/响应 Schema。

定义登录、刷新 Token、登出等接口的数据格式。
Pydantic 会自动校验请求参数的类型和长度。
"""

from pydantic import BaseModel, Field

from app.schemas.user import UserOut


class LoginRequest(BaseModel):
    """登录请求体。"""
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    """刷新 Token 请求体。"""
    refresh_token: str


class LogoutRequest(BaseModel):
    """登出请求体。"""
    refresh_token: str


class TokenData(BaseModel):
    """登录成功返回的 Token 数据。"""
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int          # Access Token 有效期（秒）
    user: UserOut | None = None  # 登录用户信息


class AccessTokenData(BaseModel):
    """刷新 Token 后返回的新 Access Token。"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
