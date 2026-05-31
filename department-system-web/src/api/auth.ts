/**
 * 认证相关 API 接口。
 *
 * 对应后端 /api/v1/auth/* 路由。
 */

import { request, unwrap } from '@/api/request'
import type { LoginPayload, LoginResult, User } from '@/types/user'

/** 登录 */
export function login(data: LoginPayload) {
  return unwrap<LoginResult>(request.post('/auth/login', data))
}

/** 刷新 Access Token */
export function refreshToken(refresh_token: string) {
  return unwrap<{ access_token: string; token_type: string; expires_in: number }>(
    request.post('/auth/refresh', { refresh_token }),
  )
}

/** 登出 */
export function logout(refresh_token: string) {
  return unwrap<null>(request.post('/auth/logout', { refresh_token }))
}

/** 获取当前用户信息（auth 路由版本） */
export function getAuthMe() {
  return unwrap<User>(request.get('/auth/me'))
}
