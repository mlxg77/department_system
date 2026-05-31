"""
宿管-楼栋关联 ORM 模型（对应 dorm_manager_buildings 表）。

记录哪个宿管负责管理哪栋宿舍楼（多对多关系的中间表）。
"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DormManagerBuilding(Base):
    __tablename__ = "dorm_manager_buildings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    manager_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    building_id: Mapped[int] = mapped_column(BigInteger, nullable=False)  # 楼栋 ID（关联楼栋表，暂未实现）
    assigned_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    manager: Mapped["User"] = relationship(back_populates="managed_buildings")


from app.models.user import User  # noqa: E402
