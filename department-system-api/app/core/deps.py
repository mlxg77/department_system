"""
FastAPI 依赖注入（Dependencies）。

提供路由守卫功能：
- get_current_user：从请求头解析 Token，获取当前登录用户
- require_roles：检查用户是否具有指定角色（权限控制）
"""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import BusinessError
from app.models.user import User, UserRole
from app.services.auth_service import AuthService

# HTTPBearer 从 Authorization: Bearer <token> 请求头中提取 Token
# auto_error=False 表示没有 Token 时不自动报错，由我们自己处理
security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    获取当前登录用户（路由守卫）。

    在需要登录才能访问的路由中使用：
        current_user: User = Depends(get_current_user)
    """
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise BusinessError(40101, "未登录或 Token 无效", http_status=401)

    user = AuthService(db).get_user_from_access_token(credentials.credentials)
    if user is None:
        raise BusinessError(40101, "未登录或 Token 无效或已过期", http_status=401)
    return user


def require_roles(*roles: UserRole):
    """
    角色权限检查（工厂函数）。

    用法：_: User = Depends(require_roles(UserRole.ADMIN))
    只有 admin 角色才能访问该路由，否则返回 403。
    """
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise BusinessError(40301, "无权限", http_status=403)
        return current_user

    return checker
