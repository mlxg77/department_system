"""
当前用户 API 路由（/me）。

所有接口都需要登录，用户只能操作自己的数据：
- GET  /me           获取个人资料
- PUT  /me           更新个人资料
- PUT  /me/password  修改密码
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.common import ResponseModel
from app.schemas.user import MeUpdate, PasswordChange, UserOut
from app.services.user_helpers import user_to_out
from app.services.user_service import UserService

router = APIRouter(prefix="/me", tags=["当前用户"])


@router.get("", response_model=ResponseModel[UserOut])
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前登录用户的完整资料。"""
    user = UserService(db)._load_user(current_user.id)
    return ResponseModel(data=user_to_out(user))


@router.put("", response_model=ResponseModel[UserOut])
def update_me(
    data: MeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新当前用户的个人资料（手机、邮箱、紧急联系人等）。"""
    user = UserService(db)._load_user(current_user.id)
    result = UserService(db).update_me(user, data)
    return ResponseModel(data=result)


@router.put("/password", response_model=ResponseModel[None])
def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """修改当前用户密码（需提供原密码）。"""
    user = UserService(db)._load_user(current_user.id)
    UserService(db).change_password(user, data)
    return ResponseModel(data=None)
