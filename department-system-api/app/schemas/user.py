"""
用户相关请求/响应 Schema。

分为三类：
- *Out：返回给前端的数据结构
- *Create：创建用户时的请求体
- *Update：更新用户时的请求体
"""

from datetime import date, datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    ADMIN = "admin"
    STUDENT = "student"
    DORM_MANAGER = "dorm_manager"


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class StudentProfileOut(BaseModel):
    """学生档案（响应）。"""
    student_no: str
    gender: Gender | None = None
    college: str | None = None
    major: str | None = None
    grade: str | None = None
    class_name: str | None = None
    emergency_contact: str | None = None
    emergency_phone: str | None = None

    model_config = {"from_attributes": True}  # 允许从 ORM 对象自动转换


class DormManagerProfileOut(BaseModel):
    """宿管档案（响应）。"""
    employee_no: str
    gender: Gender | None = None
    hire_date: date | None = None
    remark: str | None = None
    managed_buildings: list[int] | None = None

    model_config = {"from_attributes": True}


class AdminProfileOut(BaseModel):
    """管理员档案（响应）。"""
    admin_level: int
    department: str | None = None

    model_config = {"from_attributes": True}


class UserOut(BaseModel):
    """完整用户信息（含角色档案）。"""
    id: int
    username: str
    role: UserRole
    real_name: str
    phone: str | None = None
    email: str | None = None
    avatar_url: str | None = None
    status: int
    created_at: datetime | None = None
    profile: dict[str, Any] | None = None  # 根据角色不同，内容不同

    model_config = {"from_attributes": True}


class UserListItem(BaseModel):
    """用户列表项（不含档案详情，用于列表展示）。"""
    id: int
    username: str
    role: UserRole
    real_name: str
    phone: str | None = None
    status: int
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class StudentProfileCreate(BaseModel):
    """创建学生时的档案字段。"""
    student_no: str = Field(min_length=1, max_length=30)
    gender: Gender | None = None
    college: str | None = None
    major: str | None = None
    grade: str | None = None
    class_name: str | None = None
    id_card: str | None = None
    emergency_contact: str | None = None
    emergency_phone: str | None = None


class DormManagerProfileCreate(BaseModel):
    """创建宿管时的档案字段。"""
    employee_no: str = Field(min_length=1, max_length=30)
    gender: Gender | None = None
    hire_date: date | None = None
    remark: str | None = None


class AdminProfileCreate(BaseModel):
    """创建管理员时的档案字段。"""
    admin_level: int = Field(default=1, ge=1, le=9)
    department: str | None = None


class UserCreate(BaseModel):
    """管理员创建用户的请求体。"""
    role: UserRole
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=32)
    real_name: str = Field(min_length=1, max_length=50)
    phone: str | None = None
    email: EmailStr | None = None
    profile: dict[str, Any]  # 角色档案，结构随 role 不同


class UserUpdate(BaseModel):
    """管理员更新用户的请求体（所有字段可选）。"""
    real_name: str | None = Field(default=None, min_length=1, max_length=50)
    phone: str | None = None
    email: EmailStr | None = None
    profile: dict[str, Any] | None = None


class MeUpdate(BaseModel):
    """当前用户更新自己资料的请求体。"""
    phone: str | None = None
    email: EmailStr | None = None
    emergency_contact: str | None = None
    emergency_phone: str | None = None
    remark: str | None = None


class PasswordChange(BaseModel):
    """修改密码（需验证原密码）。"""
    old_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=6, max_length=32)


class PasswordReset(BaseModel):
    """管理员重置用户密码（无需原密码）。"""
    new_password: str = Field(min_length=6, max_length=32)


class StatusUpdate(BaseModel):
    """启用/禁用用户。"""
    status: Literal[0, 1]  # 只能是 0 或 1
