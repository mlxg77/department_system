"""
用户管理业务逻辑服务。

提供用户的增删改查、密码管理、状态切换等功能。
仅管理员可调用（权限控制在路由层）。
"""

from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import BusinessError
from app.core.security import hash_password, verify_password
from app.models.admin_profile import AdminProfile
from app.models.dorm_manager_profile import DormManagerProfile
from app.models.student_profile import StudentProfile
from app.models.user import Gender, User, UserRole
from app.schemas.user import (
    AdminProfileCreate,
    DormManagerProfileCreate,
    MeUpdate,
    PasswordChange,
    PasswordReset,
    StatusUpdate,
    StudentProfileCreate,
    UserCreate,
    UserListItem,
    UserOut,
    UserUpdate,
)
from app.services.user_helpers import utcnow, user_to_out


class UserService:
    """用户服务类。"""

    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int) -> UserOut:
        """获取单个用户详情。"""
        user = self._get_active_user(user_id)
        return user_to_out(user)

    def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        role: UserRole | None = None,
        status: int | None = None,
        keyword: str | None = None,
        college: str | None = None,
        grade: str | None = None,
    ) -> tuple[list[UserListItem], int]:
        """
        分页查询用户列表，支持多条件筛选。

        返回：(当前页数据列表, 总记录数)
        """
        query = select(User).where(User.deleted_at.is_(None))

        if role is not None:
            query = query.where(User.role == role)
        if status is not None:
            query = query.where(User.status == status)
        if keyword:
            # 关键词模糊搜索：用户名、姓名、手机号
            pattern = f"%{keyword}%"
            query = query.where(
                or_(
                    User.username.like(pattern),
                    User.real_name.like(pattern),
                    User.phone.like(pattern),
                )
            )
        if college or grade:
            # 按学院/年级筛选需要关联学生档案表
            query = query.join(StudentProfile, StudentProfile.user_id == User.id)
            if college:
                query = query.where(StudentProfile.college == college)
            if grade:
                query = query.where(StudentProfile.grade == grade)

        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.scalar(count_query) or 0

        users = self.db.scalars(
            query.order_by(User.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()

        items = [
            UserListItem(
                id=u.id,
                username=u.username,
                role=u.role,
                real_name=u.real_name,
                phone=u.phone,
                status=u.status,
                created_at=u.created_at,
            )
            for u in users
        ]
        return items, total

    def create_user(self, data: UserCreate) -> UserOut:
        """创建新用户（含角色档案）。"""
        existing = self.db.scalar(select(User).where(User.username == data.username))
        if existing is not None:
            raise BusinessError(40901, "用户名已存在", http_status=409)

        profile_data = self._parse_profile_for_create(data.role, data.profile)
        user = User(
            username=data.username,
            password_hash=hash_password(data.password),
            role=data.role,
            real_name=data.real_name,
            phone=data.phone,
            email=str(data.email) if data.email else None,
            status=1,
        )
        self.db.add(user)
        self.db.flush()  # flush 获取 user.id，但尚未 commit

        try:
            self._create_profile(user, profile_data)
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise BusinessError(40901, "学号/工号或用户名已存在", http_status=409) from exc

        user = self._load_user(user.id)
        return user_to_out(user)

    def update_user(self, user_id: int, data: UserUpdate) -> UserOut:
        """管理员更新用户信息。"""
        user = self._get_active_user(user_id)
        if data.real_name is not None:
            user.real_name = data.real_name
        if data.phone is not None:
            user.phone = data.phone
        if data.email is not None:
            user.email = str(data.email)

        if data.profile is not None:
            self._update_profile(user, data.profile)

        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise BusinessError(40901, "更新失败，存在唯一字段冲突", http_status=409) from exc

        user = self._load_user(user.id)
        return user_to_out(user)

    def update_me(self, user: User, data: MeUpdate) -> UserOut:
        """当前用户更新自己的资料（权限有限，只能改部分字段）。"""
        if data.phone is not None:
            user.phone = data.phone
        if data.email is not None:
            user.email = str(data.email)

        if user.role == UserRole.STUDENT and user.student_profile:
            if data.emergency_contact is not None:
                user.student_profile.emergency_contact = data.emergency_contact
            if data.emergency_phone is not None:
                user.student_profile.emergency_phone = data.emergency_phone
        elif user.role == UserRole.DORM_MANAGER and user.dorm_manager_profile:
            if data.remark is not None:
                user.dorm_manager_profile.remark = data.remark

        self.db.commit()
        user = self._load_user(user.id)
        return user_to_out(user)

    def change_password(self, user: User, data: PasswordChange) -> None:
        """用户修改自己的密码（需验证原密码）。"""
        if not verify_password(data.old_password, user.password_hash):
            raise BusinessError(40001, "原密码错误", http_status=400)
        user.password_hash = hash_password(data.new_password)
        self.db.commit()

    def reset_password(self, user_id: int, data: PasswordReset) -> None:
        """管理员重置用户密码（无需原密码）。"""
        user = self._get_active_user(user_id)
        user.password_hash = hash_password(data.new_password)
        self.db.commit()

    def update_status(self, user_id: int, data: StatusUpdate) -> UserOut:
        """启用或禁用用户。"""
        user = self._get_active_user(user_id)
        user.status = data.status
        self.db.commit()
        user = self._load_user(user.id)
        return user_to_out(user)

    def delete_user(self, user_id: int) -> None:
        """软删除用户（设置 deleted_at，不真正删除数据）。"""
        user = self._get_active_user(user_id)
        user.deleted_at = utcnow()
        self.db.commit()

    def _get_active_user(self, user_id: int) -> User:
        """获取未删除的用户，不存在则抛 404。"""
        user = self._load_user(user_id)
        if user is None:
            raise BusinessError(40401, "用户不存在", http_status=404)
        return user

    def _load_user(self, user_id: int) -> User | None:
        """从数据库加载用户及其所有关联档案。"""
        return self.db.scalar(
            select(User)
            .where(User.id == user_id, User.deleted_at.is_(None))
            .options(
                selectinload(User.student_profile),
                selectinload(User.dorm_manager_profile),
                selectinload(User.admin_profile),
                selectinload(User.managed_buildings),
            )
        )

    def _parse_profile_for_create(self, role: UserRole, profile: dict) -> dict:
        """根据角色校验并解析创建时的档案数据。"""
        if role == UserRole.STUDENT:
            return StudentProfileCreate.model_validate(profile).model_dump()
        if role == UserRole.DORM_MANAGER:
            parsed = DormManagerProfileCreate.model_validate(profile).model_dump()
            if isinstance(parsed.get("hire_date"), date):
                parsed["hire_date"] = parsed["hire_date"]
            return parsed
        if role == UserRole.ADMIN:
            return AdminProfileCreate.model_validate(profile).model_dump()
        raise BusinessError(40001, "无效的角色", http_status=400)

    def _to_gender(self, value) -> Gender | None:
        """将各种格式的性别值统一转为 Gender 枚举。"""
        if value is None:
            return None
        if isinstance(value, Gender):
            return value
        return Gender(value.value if hasattr(value, "value") else value)

    def _create_profile(self, user: User, profile_data: dict) -> None:
        """根据用户角色创建对应的扩展档案记录。"""
        if user.role == UserRole.STUDENT:
            gender = self._to_gender(profile_data.get("gender"))
            self.db.add(
                StudentProfile(
                    user_id=user.id,
                    student_no=profile_data["student_no"],
                    gender=gender,
                    college=profile_data.get("college"),
                    major=profile_data.get("major"),
                    grade=profile_data.get("grade"),
                    class_name=profile_data.get("class_name"),
                    id_card=profile_data.get("id_card"),
                    emergency_contact=profile_data.get("emergency_contact"),
                    emergency_phone=profile_data.get("emergency_phone"),
                )
            )
        elif user.role == UserRole.DORM_MANAGER:
            gender = self._to_gender(profile_data.get("gender"))
            self.db.add(
                DormManagerProfile(
                    user_id=user.id,
                    employee_no=profile_data["employee_no"],
                    gender=gender,
                    hire_date=profile_data.get("hire_date"),
                    remark=profile_data.get("remark"),
                )
            )
        elif user.role == UserRole.ADMIN:
            self.db.add(
                AdminProfile(
                    user_id=user.id,
                    admin_level=profile_data.get("admin_level", 1),
                    department=profile_data.get("department"),
                )
            )

    def _update_profile(self, user: User, profile: dict) -> None:
        """更新用户角色档案（只允许修改部分字段，学号/工号不可改）。"""
        if user.role == UserRole.STUDENT and user.student_profile:
            allowed = {"gender", "college", "major", "grade", "class_name", "emergency_contact", "emergency_phone"}
            for key, value in profile.items():
                if key in allowed:
                    if key == "gender" and value is not None:
                        user.student_profile.gender = Gender(value)
                    elif key != "gender":
                        setattr(user.student_profile, key, value)
        elif user.role == UserRole.DORM_MANAGER and user.dorm_manager_profile:
            allowed = {"gender", "hire_date", "remark"}
            for key, value in profile.items():
                if key in allowed:
                    if key == "gender" and value is not None:
                        user.dorm_manager_profile.gender = Gender(value)
                    elif key == "hire_date" and value is not None:
                        user.dorm_manager_profile.hire_date = (
                            date.fromisoformat(value) if isinstance(value, str) else value
                        )
                    elif key != "gender":
                        setattr(user.dorm_manager_profile, key, value)
        elif user.role == UserRole.ADMIN and user.admin_profile:
            allowed = {"admin_level", "department"}
            for key, value in profile.items():
                if key in allowed:
                    setattr(user.admin_profile, key, value)
