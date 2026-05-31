"""
用户数据转换辅助函数。

负责 ORM 模型 → API 响应 Schema 的转换。
"""

from datetime import datetime, timezone
from typing import Any

from app.models.admin_profile import AdminProfile
from app.models.dorm_manager_building import DormManagerBuilding
from app.models.dorm_manager_profile import DormManagerProfile
from app.models.student_profile import StudentProfile
from app.models.user import User, UserRole
from app.schemas.user import UserOut


def build_profile_dict(user: User) -> dict[str, Any] | None:
    """
    根据用户角色，将其扩展档案转为字典。

    不同角色返回不同字段：学生返回学号/学院，宿管返回工号，管理员返回级别。
    """
    if user.role == UserRole.STUDENT and user.student_profile:
        p = user.student_profile
        return {
            "student_no": p.student_no,
            "gender": p.gender.value if p.gender else None,
            "college": p.college,
            "major": p.major,
            "grade": p.grade,
            "class_name": p.class_name,
            "emergency_contact": p.emergency_contact,
            "emergency_phone": p.emergency_phone,
        }
    if user.role == UserRole.DORM_MANAGER and user.dorm_manager_profile:
        p = user.dorm_manager_profile
        building_ids = [b.building_id for b in user.managed_buildings] if user.managed_buildings else []
        return {
            "employee_no": p.employee_no,
            "gender": p.gender.value if p.gender else None,
            "hire_date": p.hire_date.isoformat() if p.hire_date else None,
            "remark": p.remark,
            "managed_buildings": building_ids or None,
        }
    if user.role == UserRole.ADMIN and user.admin_profile:
        p = user.admin_profile
        return {
            "admin_level": p.admin_level,
            "department": p.department,
        }
    return None


def user_to_out(user: User) -> UserOut:
    """将 ORM User 对象转换为 API 响应 UserOut。"""
    return UserOut(
        id=user.id,
        username=user.username,
        role=user.role,
        real_name=user.real_name,
        phone=user.phone,
        email=user.email,
        avatar_url=user.avatar_url,
        status=user.status,
        created_at=user.created_at,
        profile=build_profile_dict(user),
    )


def utcnow() -> datetime:
    """获取当前 UTC 时间（去掉时区信息，与 MySQL DATETIME 兼容）。"""
    return datetime.now(timezone.utc).replace(tzinfo=None)
