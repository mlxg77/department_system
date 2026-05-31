"""
用户管理 API 路由（/users）。

所有接口都需要 admin 角色权限。
提供用户的增删改查、状态管理、密码重置等功能。
"""

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.models.user import User, UserRole
from app.schemas.common import PageData, ResponseModel
from app.schemas.user import (
    PasswordReset,
    StatusUpdate,
    UserCreate,
    UserListItem,
    UserOut,
    UserRole as SchemaUserRole,
    UserUpdate,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("/students", response_model=ResponseModel[PageData[UserListItem]])
def list_students(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: int | None = Query(default=None),
    keyword: str | None = Query(default=None),
    college: str | None = Query(default=None),
    grade: str | None = Query(default=None),
    _: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """分页查询学生列表，支持按学院、年级筛选。"""
    items, total = UserService(db).list_users(
        page=page,
        page_size=page_size,
        role=UserRole.STUDENT,
        status=status,
        keyword=keyword,
        college=college,
        grade=grade,
    )
    return ResponseModel(
        data=PageData(items=items, total=total, page=page, page_size=page_size)
    )


@router.get("/dorm-managers", response_model=ResponseModel[PageData[UserListItem]])
def list_dorm_managers(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: int | None = Query(default=None),
    keyword: str | None = Query(default=None),
    _: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """分页查询宿管列表。"""
    items, total = UserService(db).list_users(
        page=page,
        page_size=page_size,
        role=UserRole.DORM_MANAGER,
        status=status,
        keyword=keyword,
    )
    return ResponseModel(
        data=PageData(items=items, total=total, page=page, page_size=page_size)
    )


@router.get("", response_model=ResponseModel[PageData[UserListItem]])
def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    role: SchemaUserRole | None = Query(default=None),
    status: int | None = Query(default=None),
    keyword: str | None = Query(default=None),
    college: str | None = Query(default=None),
    grade: str | None = Query(default=None),
    _: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """分页查询所有用户（可按角色筛选）。"""
    model_role = UserRole(role.value) if role else None
    items, total = UserService(db).list_users(
        page=page,
        page_size=page_size,
        role=model_role,
        status=status,
        keyword=keyword,
        college=college,
        grade=grade,
    )
    return ResponseModel(
        data=PageData(items=items, total=total, page=page, page_size=page_size)
    )


@router.post("", response_model=ResponseModel[UserOut], status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """创建新用户。"""
    result = UserService(db).create_user(data)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=ResponseModel(data=result).model_dump(mode="json"),
    )


@router.get("/{user_id}", response_model=ResponseModel[UserOut])
def get_user(
    user_id: int,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """获取单个用户详情。"""
    result = UserService(db).get_user(user_id)
    return ResponseModel(data=result)


@router.put("/{user_id}", response_model=ResponseModel[UserOut])
def update_user(
    user_id: int,
    data: UserUpdate,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """更新用户信息。"""
    result = UserService(db).update_user(user_id, data)
    return ResponseModel(data=result)


@router.patch("/{user_id}/status", response_model=ResponseModel[UserOut])
def update_user_status(
    user_id: int,
    data: StatusUpdate,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """启用或禁用用户（status: 1=正常, 0=禁用）。"""
    result = UserService(db).update_status(user_id, data)
    return ResponseModel(data=result)


@router.delete("/{user_id}", response_model=ResponseModel[None])
def delete_user(
    user_id: int,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """软删除用户。"""
    UserService(db).delete_user(user_id)
    return ResponseModel(data=None)


@router.put("/{user_id}/password/reset", response_model=ResponseModel[None])
def reset_password(
    user_id: int,
    data: PasswordReset,
    _: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    """管理员重置用户密码。"""
    UserService(db).reset_password(user_id, data)
    return ResponseModel(data=None)
