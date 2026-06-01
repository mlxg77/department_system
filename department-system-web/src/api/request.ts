/**
 * Axios HTTP 请求封装。
 *
 * 功能：
 * 1. 统一 baseURL 和超时设置
 * 2. 请求拦截器：自动在 Header 中附加 Access Token
 * 3. 响应拦截器：
 *    - 检查业务错误码（code !== 0）
 *    - Access Token 过期时自动用 Refresh Token 刷新并重试
 *    - 统一错误提示（ElMessage）
 * 4. unwrap 工具函数：从 { code, message, data } 中提取 data
 */

import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'
import type { ApiResponse } from '@/types/api'
import { API_ERROR_MESSAGES } from '@/utils/constants'
import { clearTokens, getAccessToken, getRefreshToken, setAccessToken } from '@/utils/storage'

// API 基础路径，开发环境通过 vite proxy 转发到后端
const baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

export const request = axios.create({
  baseURL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

// 防止多个请求同时触发 Token 刷新
// Promise = 「将来会出结果」的异步操作；Promise<T> = 将来成功时，结果类型是 T。
let refreshing: Promise<string | null> | null = null
//   ↑ 变量名   ↑ 类型注解                      ↑ 初始值

/** 处理业务错误：显示提示，401 时跳转登录页 */
function handleBusinessError(code: number, message: string): void {
  // 从左到右找第一个“有效值”。
  // 如果 message 为空，则使用 API_ERROR_MESSAGES 中对应的错误信息，否则使用 '操作失败'
  const text = message || API_ERROR_MESSAGES[code] || '操作失败'
  ElMessage.error(text)
  // 如果 code 为 40101 且当前路由不是登录页，则清除 Token 并跳转登录页
  if (code === 40101 && router.currentRoute.value.name !== 'login') {
    clearTokens()
    // 获取当前路由的完整路径，用于登录后重定向
    const redirect = router.currentRoute.value.fullPath
    // 如果当前路由不是登录页，则将当前路由作为参数传递给登录页，用于登录后重定向
    router.push({ name: 'login', query: redirect !== '/login' ? { redirect } : {} })
  }
}

// 请求拦截器：每个请求自动带上 Authorization Header
request.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：处理业务错误和 Token 自动刷新use = “注册一个会自动执行的函数”。
// 在 Axios（Axios = 前端用来调用后端 API 的工具库。） 里，interceptors.response.use 就是：所有响应回来后，先执行你写的这两个函数，再决定是成功还是失败。

request.interceptors.response.use(
  // 成功时执行（response = HTTP 响应对象，包含 code、message、data 等字段）
  (response) => {
    const body = response.data as ApiResponse
    // 后端返回 code !== 0 表示业务错误
    if (body && typeof body.code === 'number' && body.code !== 0) {
      handleBusinessError(body.code, body.message)
      //Promise.reject(body) = 虽然 HTTP 请求回来了，但业务失败，我要把这个异步结果标记成“错误”，让后面的 await / .catch() 知道别当成功结果处理。
      return Promise.reject(body)
    }
    return response
  },
  // 失败时执行（error = 错误对象，包含 response、config 等字段）
  async (error: AxiosError<ApiResponse>) => {
    const status = error.response?.status
    const body = error.response?.data
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
    const url = original?.url ?? ''

    // 登录失败：直接提示，不走 Token 刷新逻辑
    if (url.includes('/auth/login')) {
      ElMessage.error(body?.message || '密码错误，请重新输入')
      return Promise.reject(error)
    }

    // 401 且是 Token 过期：尝试用 Refresh Token 换取新 Access Token
    if (status === 401 && body?.code === 40101) {
      const refresh = getRefreshToken()

      // 如果 refresh token 不存在，或者已经重试过，或者请求的是刷新 token 的接口，则清除 Token 并跳转登录页
      if (!refresh || original._retry || url.includes('/auth/refresh')) {
        clearTokens()
        if (router.currentRoute.value.name !== 'login') {
          handleBusinessError(body.code, body.message)
          router.push({ name: 'login' })
        }
        return Promise.reject(error)
      }

      // 标记为已重试，用 true 表示「这个请求已经刷新过 Token 并重试过了」，防止同一个请求无限循环。
      original._retry = true

      // 多个并发 401 请求共享同一个刷新 Promise，避免重复刷新
      // 这里的做法是：第一个请求去刷新，后面的请求等着用同一个结果。
      if (!refreshing) {
        refreshing = axios
          .post<ApiResponse<{ access_token: string }>>(`${baseURL}/auth/refresh`, {
            refresh_token: refresh,
          })
          .then((res) => {
            const token = res.data.data?.access_token
            if (!token || res.data.code !== 0) throw new Error('refresh failed')
            setAccessToken(token)
            return token
          })
          .catch(() => {
            clearTokens()
            router.push({ name: 'login' })
            return null
          })
          .finally(() => {
            refreshing = null
          })
      }

      const newToken = await refreshing
      if (!newToken) return Promise.reject(error)

      // 用新 Token 重试原请求
      original.headers.Authorization = `Bearer ${newToken}`
      return request(original)
    }

    if (body?.code) {
      handleBusinessError(body.code, body.message)
    } else {
      ElMessage.error(error.message || '网络请求失败')
    }
    return Promise.reject(error)
  },
)

/** 从 API 响应中提取 data 字段，简化调用方代码 */
// 导出一个叫 unwrap 的异步函数。
// 它接收一个 Axios 请求（Promise），
// 等请求完成后，从 { code, message, data } 里取出 data，
// 返回类型是 T（由调用时指定）。
export async function unwrap<T>(promise: Promise<{ data: ApiResponse<T> }>): Promise<T> {
  const { data } = await promise
  return data.data as T
}


// Axios 是基于 Promise 封装的 HTTP 请求库。发请求时 Axios 返回 Promise，你用 await / .then() 等它完成。
// Axios 负责发 HTTP 请求，每次请求都返回一个 Promise；你用 await、.then()、unwrap 等来等这个 Promise 完成，拦截器则在 Promise 链上统一处理 Token 和错误。