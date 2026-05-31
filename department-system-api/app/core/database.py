"""
数据库连接模块。

使用 SQLAlchemy 连接 MySQL，并提供：
- engine：数据库引擎
- SessionLocal：会话工厂
- Base：所有 ORM 模型的基类
- get_db：FastAPI 依赖注入用的数据库会话生成器
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,   # 每次取连接前先 ping，避免连接已断开
    pool_recycle=3600,    # 连接池中的连接 1 小时后自动回收
)

# 会话工厂：每次调用 SessionLocal() 创建一个新的数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """所有 ORM 模型（User、StudentProfile 等）的基类。"""
    pass


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI 依赖注入函数，为每个请求提供一个数据库会话。

    用法：在路由函数参数中写 `db: Session = Depends(get_db)`
    请求结束后自动关闭会话，避免连接泄漏。
    """
    db = SessionLocal()
    try:
        yield db  # yield 之前的代码在请求开始时执行，之后的在请求结束时执行
    finally:
        db.close()
