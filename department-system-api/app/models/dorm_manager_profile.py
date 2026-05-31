"""
宿管扩展档案 ORM 模型（对应 dorm_manager_profiles 表）。

存储工号、入职日期等宿管专属信息。
"""

from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.user import Gender


class DormManagerProfile(Base):
    __tablename__ = "dorm_manager_profiles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), unique=True, nullable=False)
    employee_no: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)  # 工号（唯一）
    gender: Mapped[Gender | None] = mapped_column(
        Enum(Gender, values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    hire_date: Mapped[date | None] = mapped_column(Date, nullable=True)  # 入职日期
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="dorm_manager_profile")


from app.models.user import User  # noqa: E402
