/**
 * 认证状态管理（Pinia Store）。
 *
 * 管理当前登录用户信息和 Token 相关操作：
 * - login / logout：登录登出
 * - fetchUser：从后端获取用户信息
 * - init：应用启动时恢复登录状态
 * - isAdmin：判断当前用户是否为管理员
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as authApi from '@/api/auth'
import * as meApi from '@/api/me'
import type { LoginPayload, MeUpdatePayload, User } from '@/types/user'
import { clearTokens, getAccessToken, getRefreshToken, setTokens } from '@/utils/storage'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)       // 当前登录用户
  const initialized = ref(false)            // 是否已完成初始化

  /** 登录：调用 API → 保存 Token → 保存用户信息 */
  async function login(payload: LoginPayload) {
    const result = await authApi.login(payload)
    setTokens(result.access_token, result.refresh_token)
    user.value = result.user
    return result
  }

  /** 从后端获取当前用户信息（优先 /me，失败则尝试 /auth/me） */
  async function fetchUser() {
    try {
      user.value = await meApi.getMe()
    } catch {
      user.value = await authApi.getAuthMe()
    }
    return user.value
  }

  /** 登出：通知后端撤销 Token → 清除本地存储 */
  async function logout() {
    const refresh = getRefreshToken()
    if (refresh) {
      try {
        await authApi.logout(refresh)
      } catch {
        /* 即使后端失败也继续清除本地 Token */
      }
    }
    clearTokens()
    user.value = null
  }

  function setUser(data: User) {
    user.value = data
  }

  /** 更新个人资料并同步到 store */
  async function updateProfile(data: MeUpdatePayload) {
    const updated = await meApi.updateMe(data)
    user.value = updated
    return updated
  }

  /**
   * 应用启动时调用：如果有 Token 则尝试恢复登录状态。
   * Token 无效则清除。
   */
  async function init() {
    if (!getAccessToken() && !getRefreshToken()) {
      initialized.value = true
      return
    }
    try {
      await fetchUser()
    } catch {
      clearTokens()
      user.value = null
    } finally {
      initialized.value = true
    }
  }

  const isAdmin = () => user.value?.role === 'admin'

  return { user, initialized, login, logout, fetchUser, setUser, updateProfile, init, isAdmin }
})
