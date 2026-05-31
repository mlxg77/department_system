/**
 * 当前用户 API 接口。
 *
 * 对应后端 /api/v1/me/* 路由，用户只能操作自己的数据。
 */

import { request, unwrap } from '@/api/request'
import type { MeUpdatePayload, User } from '@/types/user'

/** 获取当前用户资料 */
export function getMe() {
  return unwrap<User>(request.get('/me'))
}

/** 更新当前用户资料 */
export function updateMe(data: MeUpdatePayload) {
  return unwrap<User>(request.put('/me', data))
}

/** 修改密码 */
export function changePassword(old_password: string, new_password: string) {
  return unwrap<null>(request.put('/me/password', { old_password, new_password }))
}
