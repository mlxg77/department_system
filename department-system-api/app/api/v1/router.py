"""
API v1 路由汇总。

将所有子路由（auth、me、users）挂载到 /api/v1 前缀下。
"""

from fastapi import APIRouter

from app.api.v1 import auth, me, users

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)   # /api/v1/auth/*
api_router.include_router(me.router)     # /api/v1/me/*
api_router.include_router(users.router)  # /api/v1/users/*
