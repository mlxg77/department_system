"""
Refresh Token ORM 模型（对应 refresh_tokens 表）。

Access Token 过期后，前端用 Refresh Token 换取新的 Access Token。
数据库只存储 Token 的 SHA256 哈希值，不存明文。
"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)  # Token 哈希
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)           # 过期时间
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)     # 撤销时间（登出时设置）
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")


from app.models.user import User  # noqa: E402
