"""
初始化脚本：创建默认超级管理员账号。

用法：python -m scripts.seed_admin
默认账号：admin / 123456
"""

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.admin_profile import AdminProfile
from app.models.user import User, UserRole


def seed_admin(username: str = "admin", password: str = "123456", real_name: str = "系统管理员") -> None:
    """如果管理员不存在则创建，已存在则跳过。"""
    db = SessionLocal()
    try:
        existing = db.scalar(select(User).where(User.username == username))
        if existing is not None:
            print(f"管理员 {username} 已存在，跳过创建")
            return

        user = User(
            username=username,
            password_hash=hash_password(password),
            role=UserRole.ADMIN,
            real_name=real_name,
            status=1,
        )
        db.add(user)
        db.flush()
        db.add(AdminProfile(user_id=user.id, admin_level=9, department="学生处"))
        db.commit()
        print(f"已创建超级管理员: {username} / {password}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
