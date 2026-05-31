"""
应用配置模块。

从 .env 文件或环境变量中读取配置项，
所有模块通过 `from app.core.config import settings` 使用统一配置。
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类，字段名对应 .env 中的变量名（大写）。"""

    # 自动从项目根目录的 .env 文件加载配置
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # 数据库连接字符串（MySQL + PyMySQL 驱动）
    DATABASE_URL: str = "mysql+pymysql://department:department@120.26.150.7:3306/department?charset=utf8mb4"
    # JWT 签名密钥（生产环境务必改为随机长字符串）
    SECRET_KEY: str = "change-me-in-production-use-a-long-random-string"
    # Access Token 有效期（分钟）
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    # Refresh Token 有效期（天）
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    # JWT 加密算法
    ALGORITHM: str = "HS256"


# 全局单例，整个应用共享同一份配置
settings = Settings()
