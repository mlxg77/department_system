"""
安全相关工具函数。

包含：
- 密码哈希与验证（bcrypt）
- JWT Access Token 的创建与解析
- Refresh Token 的生成与哈希
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    """将明文密码加密为 bcrypt 哈希值，存入数据库。"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码是否与数据库中的哈希值匹配。"""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(user_id: int, role: str) -> str:
    """
    创建 JWT Access Token。

    payload 中包含用户 ID（sub）、角色（role）、过期时间（exp）。
    前端每次请求 API 时在 Header 中携带：Authorization: Bearer <token>
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),   # subject，即用户 ID
        "role": role,
        "exp": expire,         # expiration，过期时间
        "iat": datetime.now(timezone.utc),  # issued at，签发时间
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """解析 JWT Token，成功返回 payload 字典，失败（过期/篡改）返回 None。"""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


def generate_refresh_token() -> str:
    """生成随机 Refresh Token 明文（48 字节 URL 安全字符串）。"""
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    """
    对 Refresh Token 做 SHA256 哈希后存入数据库。

    数据库只存哈希值，不存明文，即使数据库泄露也无法直接使用 Token。
    """
    return hashlib.sha256(token.encode()).hexdigest()
