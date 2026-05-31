# 用户管理 — API 接口设计

**Base URL:** `/api/v1`  
**认证方式:** `Authorization: Bearer <access_token>`

---

## 统一响应格式

### 成功响应

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

### 分页响应

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

### 错误码

| code | 含义 |
|------|------|
| 0 | 成功 |
| 40001 | 参数校验失败 |
| 40101 | 未登录 / Token 无效或过期 |
| 40301 | 无权限 |
| 40401 | 资源不存在 |
| 40901 | 用户名/学号/工号已存在 |
| 50001 | 服务器内部错误 |

---

## 模块 1：认证 `/api/v1/auth`

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| POST | `/auth/login` | 公开 | 登录 |
| POST | `/auth/refresh` | 公开 | 刷新 Access Token |
| POST | `/auth/logout` | 已登录 | 注销（吊销 Refresh Token） |
| GET | `/auth/me` | 已登录 | 获取当前用户信息 |

### POST `/auth/login`

**Request:**

```json
{
  "username": "2023001001",
  "password": "123456"
}
```

**Response:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": 1,
      "username": "2023001001",
      "role": "student",
      "real_name": "张三",
      "phone": "13800138000",
      "email": null,
      "avatar_url": null,
      "status": 1,
      "profile": {
        "student_no": "2023001001",
        "gender": "male",
        "college": "计算机学院",
        "major": "软件工程",
        "grade": "2023",
        "class_name": "软工2301"
      }
    }
  }
}
```

### POST `/auth/refresh`

**Request:**

```json
{
  "refresh_token": "eyJ..."
}
```

**Response:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

### POST `/auth/logout`

**Request:**

```json
{
  "refresh_token": "eyJ..."
}
```

**Response:**

```json
{
  "code": 0,
  "message": "success",
  "data": null
}
```

### GET `/auth/me`

返回当前登录用户完整信息，按角色附带对应 `profile`：

- `student` → `student_profiles` 字段
- `dorm_manager` → `dorm_manager_profiles` 字段 + 可选 `managed_buildings`
- `admin` → `admin_profiles` 字段

---

## 模块 2：当前用户 `/api/v1/me`

| 方法 | 路径 | 权限 | 说明 |
|------|------|------|------|
| GET | `/me` | 已登录 | 获取本人资料（同 `/auth/me`） |
| PUT | `/me` | 已登录 | 修改本人资料（不可改 role/username） |
| PUT | `/me/password` | 已登录 | 修改密码 |
| POST | `/me/avatar` | 已登录 | 上传头像（可选，后续实现） |

### PUT `/me`

**Request（学生示例）:**

```json
{
  "phone": "13800138000",
  "email": "zhangsan@example.com",
  "emergency_contact": "张父",
  "emergency_phone": "13900139000"
}
```

**Response:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "username": "2023001001",
    "role": "student",
    "real_name": "张三",
    "phone": "13800138000",
    "email": "zhangsan@example.com",
    "profile": { }
  }
}
```

### PUT `/me/password`

**Request:**

```json
{
  "old_password": "123456",
  "new_password": "654321"
}
```

**Response:**

```json
{
  "code": 0,
  "message": "success",
  "data": null
}
```

---

## 模块 3：用户管理 `/api/v1/users`（仅 admin）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/users` | 用户列表（分页、筛选） |
| POST | `/users` | 创建用户 |
| GET | `/users/{user_id}` | 用户详情 |
| PUT | `/users/{user_id}` | 更新用户 |
| PATCH | `/users/{user_id}/status` | 启用/禁用 |
| DELETE | `/users/{user_id}` | 软删除 |
| PUT | `/users/{user_id}/password/reset` | 重置密码 |
| GET | `/users/students` | 学生列表（快捷入口） |
| GET | `/users/dorm-managers` | 宿管列表（快捷入口） |

### GET `/users`

**Query 参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1 |
| page_size | int | 否 | 每页条数，默认 20，最大 100 |
| role | string | 否 | `admin` / `student` / `dorm_manager` |
| status | int | 否 | 1 正常 / 0 禁用 |
| keyword | string | 否 | 模糊搜索 username、real_name、phone |
| college | string | 否 | 学生：按学院筛选 |
| grade | string | 否 | 学生：按年级筛选 |

**Response:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "username": "2023001001",
        "role": "student",
        "real_name": "张三",
        "phone": "13800138000",
        "status": 1,
        "created_at": "2026-01-01T08:00:00"
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

### POST `/users`

#### 创建学生

**Request:**

```json
{
  "role": "student",
  "username": "2023001001",
  "password": "123456",
  "real_name": "张三",
  "phone": "13800138000",
  "email": null,
  "profile": {
    "student_no": "2023001001",
    "gender": "male",
    "college": "计算机学院",
    "major": "软件工程",
    "grade": "2023",
    "class_name": "软工2301"
  }
}
```

#### 创建宿管

**Request:**

```json
{
  "role": "dorm_manager",
  "username": "SG001",
  "password": "123456",
  "real_name": "李阿姨",
  "phone": "13700137000",
  "profile": {
    "employee_no": "SG001",
    "gender": "female",
    "hire_date": "2020-09-01"
  }
}
```

#### 创建管理员

**Request:**

```json
{
  "role": "admin",
  "username": "admin02",
  "password": "123456",
  "real_name": "王管理",
  "profile": {
    "admin_level": 1,
    "department": "学生处"
  }
}
```

**Response（201）:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 10,
    "username": "2023001001",
    "role": "student",
    "real_name": "张三",
    "status": 1,
    "profile": { }
  }
}
```

### GET `/users/{user_id}`

返回指定用户完整信息（含 profile）。

### PUT `/users/{user_id}`

更新用户基础信息与 profile，不可修改 `role`（如需改角色，建议新建账号）。

**Request:**

```json
{
  "real_name": "张三",
  "phone": "13800138001",
  "email": "zhangsan@example.com",
  "profile": {
    "college": "计算机学院",
    "major": "软件工程",
    "grade": "2023",
    "class_name": "软工2301"
  }
}
```

### PATCH `/users/{user_id}/status`

**Request:**

```json
{
  "status": 0
}
```

### DELETE `/users/{user_id}`

软删除用户，设置 `deleted_at`，返回：

```json
{
  "code": 0,
  "message": "success",
  "data": null
}
```

### PUT `/users/{user_id}/password/reset`

管理员重置他人密码，无需旧密码。

**Request:**

```json
{
  "new_password": "123456"
}
```

---

## 接口清单速查

```
公开
  POST   /api/v1/auth/login
  POST   /api/v1/auth/refresh

已登录（所有角色）
  POST   /api/v1/auth/logout
  GET    /api/v1/auth/me
  GET    /api/v1/me
  PUT    /api/v1/me
  PUT    /api/v1/me/password
  POST   /api/v1/me/avatar          [可选，后续实现]

仅管理员
  GET    /api/v1/users
  POST   /api/v1/users
  GET    /api/v1/users/{id}
  PUT    /api/v1/users/{id}
  PATCH  /api/v1/users/{id}/status
  DELETE /api/v1/users/{id}
  PUT    /api/v1/users/{id}/password/reset
  GET    /api/v1/users/students
  GET    /api/v1/users/dorm-managers
```

---

## HTTP 状态码映射

| 场景 | HTTP Status |
|------|-------------|
| 成功 | 200 |
| 创建成功 | 201 |
| 参数错误 | 422 |
| 未认证 | 401 |
| 无权限 | 403 |
| 资源不存在 | 404 |
| 唯一约束冲突 | 409 |
| 服务器错误 | 500 |
