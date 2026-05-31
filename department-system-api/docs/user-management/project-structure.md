# 用户管理 — FastAPI 项目目录结构

推荐在 `department-system-api` 下按以下结构组织代码：

```
department-system-api/
├── app/
│   ├── main.py                 # FastAPI 应用入口
│   ├── core/
│   │   ├── config.py           # 数据库、JWT、CORS 等配置
│   │   ├── security.py         # 密码哈希、JWT 生成/校验
│   │   ├── deps.py             # 依赖注入：get_current_user, require_roles
│   │   └── database.py         # SQLAlchemy engine / session
│   ├── models/
│   │   ├── user.py
│   │   ├── student_profile.py
│   │   ├── dorm_manager_profile.py
│   │   ├── admin_profile.py
│   │   └── refresh_token.py
│   ├── schemas/
│   │   ├── common.py           # 统一响应、分页参数
│   │   ├── auth.py             # LoginRequest, TokenResponse
│   │   └── user.py             # UserCreate, UserUpdate, UserOut
│   ├── api/
│   │   └── v1/
│   │       ├── router.py         # 汇总 v1 路由
│   │       ├── auth.py
│   │       ├── me.py
│   │       └── users.py
│   └── services/
│       ├── auth_service.py
│       └── user_service.py
├── alembic/                    # 数据库迁移（可选）
├── requirements.txt
└── .env                        # 环境变量（不入库）
```

---

## 核心 Schema 示例

```python
from enum import Enum
from typing import Optional, Literal
from pydantic import BaseModel, Field


class UserRole(str, Enum):
    ADMIN = "admin"
    STUDENT = "student"
    DORM_MANAGER = "dorm_manager"


class StudentProfileCreate(BaseModel):
    student_no: str
    gender: Optional[Literal["male", "female", "other"]] = None
    college: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[str] = None
    class_name: Optional[str] = None


class DormManagerProfileCreate(BaseModel):
    employee_no: str
    gender: Optional[Literal["male", "female", "other"]] = None
    hire_date: Optional[str] = None


class AdminProfileCreate(BaseModel):
    admin_level: int = 1
    department: Optional[str] = None


class UserCreate(BaseModel):
    role: UserRole
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=32)
    real_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    profile: dict  # 按 role 校验，或使用 Union + discriminator
```

---

## 权限依赖注入示例

```python
from fastapi import Depends, HTTPException, status


def require_roles(*roles: UserRole):
    def checker(current_user=Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限",
            )
        return current_user
    return checker


# 使用示例：仅管理员可访问
@router.get("/users")
async def list_users(user=Depends(require_roles(UserRole.ADMIN))):
    ...
```

---

## 统一响应封装示例

```python
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    code: int = 0
    message: str = "success"
    data: Optional[T] = None


class PageData(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
```

---

## 推荐依赖包

```txt
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.0
pymysql>=1.1.0          # MySQL 驱动
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
pydantic-settings>=2.0.0
python-multipart>=0.0.9  # 文件上传
alembic>=1.13.0          # 数据库迁移（可选）
```

---

## 环境变量示例（.env）

```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/dorm_system
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
```
