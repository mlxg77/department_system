"""
认证相关 API 路由。

接口列表：
- POST /auth/login    登录
- POST /auth/refresh  刷新 Token
- POST /auth/logout   登出
- GET  /auth/me       获取当前用户信息
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.auth import (
    AccessTokenData,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    TokenData,
)
from app.schemas.common import ResponseModel
from app.schemas.user import UserOut
from app.services.auth_service import AuthService
from app.services.user_helpers import user_to_out
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=ResponseModel[TokenData])
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """用户登录，返回 Access Token + Refresh Token + 用户信息。"""
    result = AuthService(db).login(data)
    return ResponseModel(data=result)


@router.post("/refresh", response_model=ResponseModel[AccessTokenData])
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    """Access Token 过期后，用 Refresh Token 换取新的 Access Token。"""
    result = AuthService(db).refresh(data.refresh_token)
    return ResponseModel(data=result)


@router.post("/logout", response_model=ResponseModel[None])
def logout(data: LogoutRequest, db: Session = Depends(get_db)):
    """登出，撤销 Refresh Token。"""
    AuthService(db).logout(data.refresh_token)
    return ResponseModel(data=None)


@router.get("/me", response_model=ResponseModel[UserOut])
def auth_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前登录用户的完整信息（需要 Token）。"""
    user = UserService(db)._load_user(current_user.id)
    return ResponseModel(data=user_to_out(user))
