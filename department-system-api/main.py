"""
项目根目录入口文件。

运行 `uvicorn main:app --reload` 时会加载此文件，
它从 app.main 中导出 FastAPI 应用实例 app。
"""

from app.main import app

__all__ = ["app"]
