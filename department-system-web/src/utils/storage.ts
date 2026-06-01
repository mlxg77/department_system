/**
 * Token 本地存储（localStorage）
 *
 * 存哪：用户电脑上的浏览器，按网站域名隔离，不会自动上传到服务器。
 * 谁读：request.ts 拦截器取出后放进 Authorization 请求头。
 *
 * 为何用 localStorage（简要）：
 * - 刷新/关闭浏览器后再打开，登录态仍可保留（配合 Refresh Token）
 * - 与 Axios 手动带 Bearer Token 的方式简单匹配
 *
 * 为何不用 sessionStorage：关标签页即清空，用户需频繁重新登录。
 * 为何不用 Cookie：也可行，但跨域与 HttpOnly 配置更复杂；当前项目用 Header 传 Token 即可。
 */

/** Access Token：短期凭证，每次 API 请求都会带上 */
const ACCESS_TOKEN_KEY = 'ds_access_token'
/** Refresh Token：长期凭证，仅用于 Access Token 过期时换新 */
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

/** 登录成功时同时写入两个 Token */
export function setTokens(access: string, refresh: string): void {
  setAccessToken(access)
  setRefreshToken(refresh)
}

/** 登出或 Token 失效时清空，避免继续以过期身份请求 */
export function clearTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}
