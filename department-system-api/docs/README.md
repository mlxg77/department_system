# 学生公寓管理系统 — 设计文档

基于 FastAPI 的后端设计文档，按模块拆分存放。

## 文档目录

| 文档 | 说明 |
|------|------|
| [用户管理模块总览](./user-management/README.md) | 设计原则、角色权限、JWT、业务规则 |
| [数据库表结构](./user-management/database-schema.md) | 用户管理相关 SQL 建表语句 |
| [API 接口设计](./user-management/api-design.md) | RESTful 接口、请求/响应示例 |
| [项目目录结构](./user-management/project-structure.md) | FastAPI 推荐代码组织 |

## 技术栈

- **后端框架**: FastAPI
- **数据库**: MySQL 8.0+ / PostgreSQL（推荐 MySQL）
- **ORM**: SQLAlchemy 2.0
- **认证**: JWT（Access Token + Refresh Token）
- **密码**: bcrypt

## 当前进度

- [x] 用户管理 — 设计文档
- [ ] 用户管理 — 后端实现
- [ ] 宿舍管理 — 设计文档
- [ ] 报修管理 — 设计文档
