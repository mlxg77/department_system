"""
管理员扩展档案 ORM 模型（对应 admin_profiles 表）。

每个 admin 角色的用户有且仅有一条管理员档案记录。
"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AdminProfile(Base):
    __tablename__ = "admin_profiles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), unique=True, nullable=False)
    admin_level: Mapped[int] = mapped_column(nullable=False, default=1)  # 管理级别 1-9
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)  # 所属部门
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="admin_profile")


from app.models.user import User  # noqa: E402
