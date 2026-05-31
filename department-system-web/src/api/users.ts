/**
 * 用户管理 API 接口（管理员专用）。
 *
 * 对应后端 /api/v1/users/* 路由。
 */

import { request, unwrap } from '@/api/request'
import type { PageData } from '@/types/api'
import type {
  User,
  UserCreatePayload,
  UserListItem,
  UserListQuery,
  UserUpdatePayload,
} from '@/types/user'

/** 分页查询所有用户 */
export function listUsers(params: UserListQuery) {
  return unwrap<PageData<UserListItem>>(request.get('/users', { params }))
}

/** 分页查询学生 */
export function listStudents(params: UserListQuery) {
  return unwrap<PageData<UserListItem>>(request.get('/users/students', { params }))
}

/** 分页查询宿管 */
export function listDormManagers(params: UserListQuery) {
  return unwrap<PageData<UserListItem>>(request.get('/users/dorm-managers', { params }))
}

/** 获取用户详情 */
export function getUser(userId: number) {
  return unwrap<User>(request.get(`/users/${userId}`))
}

/** 创建用户 */
export function createUser(data: UserCreatePayload) {
  return unwrap<User>(request.post('/users', data))
}

/** 更新用户 */
export function updateUser(userId: number, data: UserUpdatePayload) {
  return unwrap<User>(request.put(`/users/${userId}`, data))
}

/** 启用/禁用用户 */
export function updateUserStatus(userId: number, status: 0 | 1) {
  return unwrap<User>(request.patch(`/users/${userId}/status`, { status }))
}

/** 软删除用户 */
export function deleteUser(userId: number) {
  return unwrap<null>(request.delete(`/users/${userId}`))
}

/** 重置用户密码 */
export function resetUserPassword(userId: number, new_password: string) {
  return unwrap<null>(request.put(`/users/${userId}/password/reset`, { new_password }))
}
