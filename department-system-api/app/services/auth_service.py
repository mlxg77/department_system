"""
认证业务逻辑服务。

处理登录、Token 刷新、登出等认证相关操作。
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BusinessError
from app.core.security import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import AccessTokenData, LoginRequest, TokenData
from app.services.user_helpers import utcnow, user_to_out


class AuthService:
    """认证服务类，每个实例绑定一个数据库会话。"""

    def __init__(self, db: Session):
        self.db = db

    def login(self, data: LoginRequest) -> TokenData:
        """
        用户登录。

        流程：查用户 → 验密码 → 检查状态 → 生成 Token → 返回
        """
        user = self.db.scalar(
            select(User).where(User.username == data.username, User.deleted_at.is_(None))
        )
        if user is None or not verify_password(data.password, user.password_hash):
            raise BusinessError(40101, "用户名或密码错误", http_status=401)
        if user.status != 1:
            raise BusinessError(40301, "账号已被禁用", http_status=403)

        user.last_login_at = utcnow()
        access_token = create_access_token(user.id, user.role.value)
        refresh_token = self._create_refresh_token(user.id)
        self.db.commit()
        self.db.refresh(user)

        return TokenData(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_to_out(user),
        )

    def refresh(self, refresh_token: str) -> AccessTokenData:
        """用 Refresh Token 换取新的 Access Token。"""
        token_hash = hash_refresh_token(refresh_token)
        record = self.db.scalar(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        if record is None or record.revoked_at is not None:
            raise BusinessError(40101, "Refresh Token 无效", http_status=401)
        if record.expires_at < utcnow():
            raise BusinessError(40101, "Refresh Token 已过期", http_status=401)

        user = self.db.get(User, record.user_id)
        if user is None or user.deleted_at is not None or user.status != 1:
            raise BusinessError(40101, "用户不存在或已禁用", http_status=401)

        access_token = create_access_token(user.id, user.role.value)
        return AccessTokenData(
            access_token=access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    def logout(self, refresh_token: str) -> None:
        """登出：撤销 Refresh Token（标记 revoked_at）。"""
        token_hash = hash_refresh_token(refresh_token)
        record = self.db.scalar(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        if record is not None and record.revoked_at is None:
            record.revoked_at = utcnow()
            self.db.commit()

    def get_user_from_access_token(self, token: str) -> User | None:
        """从 Access Token 解析出用户对象，Token 无效时返回 None。"""
        payload = decode_access_token(token)
        if payload is None:
            return None
        user_id = payload.get("sub")
        if user_id is None:
            return None
        user = self.db.get(User, int(user_id))
        if user is None or user.deleted_at is not None or user.status != 1:
            return None
        return user

    def _create_refresh_token(self, user_id: int) -> str:
        """生成 Refresh Token 并存入数据库，返回明文 Token 给前端。"""
        plain_token = generate_refresh_token()
        expires_at = utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        record = RefreshToken(
            user_id=user_id,
            token_hash=hash_refresh_token(plain_token),
            expires_at=expires_at,
        )
        self.db.add(record)
        return plain_token
