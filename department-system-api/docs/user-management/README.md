# 用户管理模块 — 总览

学生公寓管理系统的第一步：用户管理。用户分为三类：**管理员**、**学生**、**宿管阿姨**。

## 设计原则

| 原则 | 说明 |
|------|------|
| 统一认证，分角色授权 | 所有角色共用登录/Token 机制，业务接口按角色控制访问 |
| 基础表 + 扩展表 | `users` 存通用字段，学生/宿管/管理员各自扩展业务字段 |
| RESTful + 统一响应 | 路径语义清晰，错误码与分页格式统一 |
| 可扩展 | 后续可接入宿舍、报修、访客等模块，无需改动用户核心结构 |

## 角色定义

| 角色 | 枚举值 | 典型权限 |
|------|--------|----------|
| 管理员 | `admin` | 用户 CRUD、重置密码、启用/禁用、查看全部用户 |
| 学生 | `student` | 查看/修改本人资料、修改密码 |
| 宿管阿姨 | `dorm_manager` | 查看/修改本人资料、修改密码；后续管理所负责楼栋的学生 |

## 权限矩阵（用户管理模块）

| 接口 | admin | student | dorm_manager |
|------|:-----:|:-------:|:------------:|
| 登录 / 刷新 Token | ✓ | ✓ | ✓ |
| 查看/修改本人资料 | ✓ | ✓ | ✓ |
| 修改本人密码 | ✓ | ✓ | ✓ |
| 创建用户 | ✓ | ✗ | ✗ |
| 用户列表 / 详情 | ✓ | ✗ | ✗ |
| 更新/禁用/删除用户 | ✓ | ✗ | ✗ |
| 重置他人密码 | ✓ | ✗ | ✗ |

## 表关系

```
users (1) ── (0..1) student_profiles
users (1) ── (0..1) dorm_manager_profiles
users (1) ── (0..1) admin_profiles
users (1) ── (N)    refresh_tokens
users (1) ── (N)    dorm_manager_buildings   [宿管专用，预留]
```

## JWT 配置建议

| 项 | 建议值 |
|----|--------|
| Access Token 有效期 | 1 ~ 2 小时 |
| Refresh Token 有效期 | 7 ~ 30 天 |
| Payload 字段 | `sub`(user_id), `role`, `exp`, `iat` |
| 密码哈希算法 | bcrypt |

## 业务规则

1. **创建用户**：同一事务内写入 `users` + 对应 `*_profiles` 表；`role` 与 profile 类型必须一致。
2. **username 唯一**：全局唯一；软删除用户的 username 建议永久占用，避免混淆。
3. **禁用用户**：`status = 0` 时拒绝登录，但不删除数据。
4. **软删除**：设置 `deleted_at`，列表默认过滤已删除用户；禁止已删除用户登录。
5. **宿管楼栋**：创建宿管时可传 `building_ids`（可选），写入 `dorm_manager_buildings`。
6. **初始管理员**：首次部署通过 seed 脚本或环境变量创建超级管理员。

## 后续可扩展

- **宿舍模块**：`buildings`、`rooms`、`dorm_assignments` 关联 `student_profiles.user_id`
- **操作日志**：`audit_logs` 记录管理员对用户的关键操作
- **批量导入**：`POST /users/import` 上传 Excel 批量创建学生
- **找回密码**：短信/邮件验证码流程

## 相关文档

- [数据库表结构](./database-schema.md)
- [API 接口设计](./api-design.md)
- [项目目录结构](./project-structure.md)
