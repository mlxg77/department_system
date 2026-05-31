"""
FastAPI 应用主入口。

负责：
1. 创建 FastAPI 实例
2. 配置 CORS（允许前端跨域访问）
3. 注册全局异常处理器
4. 挂载所有 API 路由
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.exceptions import BusinessError, business_error_handler, validation_error_handler

# 创建 FastAPI 应用，title/version 会显示在自动生成的 API 文档 (/docs) 中
app = FastAPI(
    title="学生公寓管理系统 API",
    version="1.0.0",
    description="用户管理模块 API",
)

# CORS 中间件：允许浏览器前端（如 localhost:5173）调用后端 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # 允许所有来源（生产环境建议改为具体域名）
    allow_credentials=True,
    allow_methods=["*"],       # 允许 GET/POST/PUT/DELETE 等所有 HTTP 方法
    allow_headers=["*"],       # 允许所有请求头（包括 Authorization）
)

# 注册自定义异常处理器，统一返回 { code, message, data } 格式
app.add_exception_handler(BusinessError, business_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)

# 挂载 v1 版本的所有路由，前缀为 /api/v1
app.include_router(api_router)


@app.get("/")
async def root():
    """健康检查接口，访问根路径时返回欢迎信息。"""
    return {"message": "学生公寓管理系统 API", "docs": "/docs"}
