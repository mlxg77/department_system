"""
用户 ORM 模型（对应数据库 users 表）。

系统有三种角色：管理员(admin)、学生(student)、宿管(dorm_manager)。
每种角色有对应的扩展档案表（admin_profiles / student_profiles / dorm_manager_profiles）。
"""

import enum
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(str, enum.Enum):
    """用户角色枚举。"""
    ADMIN = "admin"           # 管理员
    STUDENT = "student"       # 学生
    DORM_MANAGER = "dorm_manager"  # 宿管


class Gender(str, enum.Enum):
    """性别枚举。"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class User(Base):
    """用户主表，存储所有角色的公共信息。"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # 登录用户名
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)       # 加密后的密码
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    real_name: Mapped[str] = mapped_column(String(50), nullable=False)   # 真实姓名
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[int] = mapped_column(nullable=False, default=1)       # 1=正常, 0=禁用
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)  # 软删除标记

    # 关联关系：一个用户对应一份角色档案（一对一）
    student_profile: Mapped["StudentProfile | None"] = relationship(
        back_populates="user", uselist=False, lazy="joined"
    )
    dorm_manager_profile: Mapped["DormManagerProfile | None"] = relationship(
        back_populates="user", uselist=False, lazy="joined"
    )
    admin_profile: Mapped["AdminProfile | None"] = relationship(
        back_populates="user", uselist=False, lazy="joined"
    )
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user")
    managed_buildings: Mapped[list["DormManagerBuilding"]] = relationship(back_populates="manager")


# 延迟导入，避免循环引用（User 引用 Profile，Profile 又引用 User）
from app.models.admin_profile import AdminProfile  # noqa: E402, F401
from app.models.dorm_manager_building import DormManagerBuilding  # noqa: E402, F401
from app.models.dorm_manager_profile import DormManagerProfile  # noqa: E402, F401
from app.models.refresh_token import RefreshToken  # noqa: E402, F401
from app.models.student_profile import StudentProfile  # noqa: E402, F401
