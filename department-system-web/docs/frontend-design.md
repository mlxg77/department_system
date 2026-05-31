# 前端设计说明（一期 · 用户管理）

技术栈：**Vue 3 + TypeScript + Vite + Element Plus + Pinia + Vue Router + Axios**

## 信息架构

| 模块 | 路由 | 角色 | 对应 API |
|------|------|------|----------|
| 登录 | `/login` | 公开 | `POST /auth/login` |
| 首页 | `/dashboard` | 全部 | `GET /auth/me` |
| 个人资料 | `/profile` | 全部 | `GET/PUT /me` |
| 修改密码 | `/profile/password` | 全部 | `PUT /me/password` |
| 用户管理 | `/admin/users` | admin | `GET/POST/PUT/PATCH/DELETE /users` |
| 学生管理 | `/admin/students` | admin | `GET /users/students` + 共用 CRUD |
| 宿管管理 | `/admin/dorm-managers` | admin | `GET /users/dorm-managers` + 共用 CRUD |

## 目录结构

```
src/
├── api/           # 接口封装（auth / me / users + axios 拦截器）
├── types/         # 与后端 Schema 对齐的类型
├── stores/        # Pinia：auth 登录态
├── router/        # 路由与守卫（登录、admin 权限）
├── layouts/       # 主布局（侧栏 + 顶栏）
├── views/         # 页面
├── components/    # 可复用组件（用户表单、角色档案字段）
└── utils/         # 常量、Token 存储
```

## 认证流程

1. 登录成功 → 本地存储 `access_token`、`refresh_token`
2. 请求头自动附加 `Authorization: Bearer <access_token>`
3. 业务码 `40101` 或 HTTP 401 → 使用 `refresh_token` 调用 `/auth/refresh` → 重试原请求
4. 退出 → `POST /auth/logout` 并清除本地 Token

## 开发联调

- 开发环境通过 Vite 代理：`/api` → `http://127.0.0.1:8000`
- 环境变量：`VITE_API_BASE_URL=/api/v1`（见 `.env.development`）

```bash
# 终端 1：后端
cd department-system-api && uvicorn main:app --reload

# 终端 2：前端
cd department-system-web && npm run dev
```
