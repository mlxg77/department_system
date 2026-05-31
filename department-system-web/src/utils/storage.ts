/**
 * Token 本地存储工具。
 *
 * 使用 localStorage 持久化 Access Token 和 Refresh Token，
 * 页面刷新后仍保持登录状态。
 */

const ACCESS_TOKEN_KEY = 'ds_access_token'
const REFRESH_TOKEN_KEY = 'ds_refresh_token'

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function setAccessToken(token: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, token)
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

export function setRefreshToken(token: string): void {
  localStorage.setItem(REFRESH_TOKEN_KEY, token)
}

/** 同时保存两个 Token（登录成功时调用） */
export function setTokens(access: string, refresh: string): void {
  setAccessToken(access)
  setRefreshToken(refresh)
}

/** 清除所有 Token（登出或 Token 失效时调用） */
export function clearTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}
