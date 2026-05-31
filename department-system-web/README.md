# 学生公寓管理系统 — 前端

Vue 3 + Element Plus，对接 `department-system-api` 一期用户管理接口。

## 快速开始

```bash
npm install
npm run dev
```

确保后端已启动（默认 `http://127.0.0.1:8000`），开发环境通过 Vite 代理访问 `/api/v1`。

## 文档

- [前端设计说明](./docs/frontend-design.md)
- 后端 API：[api-design.md](../department-system-api/docs/user-management/api-design.md)

## 默认账号

使用后端 `scripts/seed_admin.py` 创建的管理员账号登录，即可访问「用户 / 学生 / 宿管」管理菜单。
