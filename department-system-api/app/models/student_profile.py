"""
学生扩展档案 ORM 模型（对应 student_profiles 表）。

存储学号、学院、专业、年级等学籍信息。
"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.user import Gender


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), unique=True, nullable=False)
    student_no: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)  # 学号（唯一）
    gender: Mapped[Gender | None] = mapped_column(
        Enum(Gender, values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )
    college: Mapped[str | None] = mapped_column(String(100), nullable=True)   # 学院
    major: Mapped[str | None] = mapped_column(String(100), nullable=True)     # 专业
    grade: Mapped[str | None] = mapped_column(String(20), nullable=True)      # 年级
    class_name: Mapped[str | None] = mapped_column(String(50), nullable=True) # 班级
    id_card: Mapped[str | None] = mapped_column(String(18), nullable=True)    # 身份证号
    emergency_contact: Mapped[str | None] = mapped_column(String(50), nullable=True)  # 紧急联系人
    emergency_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)    # 紧急联系电话
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="student_profile")


from app.models.user import User  # noqa: E402
