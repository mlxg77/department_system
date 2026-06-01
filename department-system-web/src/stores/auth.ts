/**
 * 认证状态管理（Pinia Store）。
 *
 * Pinia Store 可以理解为整个应用共用的「数据仓库 + 操作手册」：
 * - 数据（state）：多处组件都要读写的共享状态，统一放在这里
 * - 方法（actions）：修改这些状态的业务逻辑，也集中在这里
 *
 * 本 Store 专门管理登录相关的一切，包括当前用户信息和 Token。
 * 登录页、布局、路由守卫、个人资料页等都会通过 useAuthStore() 来读写。
 *
 * 使用示例：
 *   import { useAuthStore } from '@/stores/auth'
 *   const auth = useAuthStore()
 *   console.log(auth.user)          // 读数据
 *   await auth.login({ ... })       // 调方法
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as authApi from '@/api/auth'
import * as meApi from '@/api/me'
import type { LoginPayload, MeUpdatePayload, User } from '@/types/user'
import { clearTokens, getAccessToken, getRefreshToken, setTokens } from '@/utils/storage'

/**
 * 定义名为 'auth' 的 Store。
 * defineStore 的第一个参数是 Store 的唯一 ID，第二个参数是 Setup 函数。
 * 函数里用 ref 定义状态、用 function 定义方法，最后 return 出去供组件使用。
 */
export const useAuthStore = defineStore('auth', () => {
  // ── 状态（state）：整个应用共享的数据 ──

  /** 当前登录用户；未登录时为 null */
  const user = ref<User | null>(null)

  /**
   * 是否已完成启动初始化。
   * 路由守卫会等 init() 跑完再决定是否放行，避免刷新页面时误判为未登录。
   */
  const initialized = ref(false)

  // ── 方法（actions）：读写状态的业务逻辑 ──

  /**
   * 登录：调后端接口 → 把 Token 存到 localStorage → 更新 user。
   * 登录页 LoginView 调用此方法。
   */
  async function login(payload: LoginPayload) {
    const result = await authApi.login(payload)
    setTokens(result.access_token, result.refresh_token)
    user.value = result.user
    return result
  }

  /**
   * 从后端拉取当前用户信息并写入 user。
   * 优先请求 /me，失败则降级到 /auth/me。
   */
  async function fetchUser() {
    try {
      user.value = await meApi.getMe()
    } catch {
      user.value = await authApi.getAuthMe()
    }
    return user.value
  }

  /**
   * 登出：通知后端撤销 Refresh Token → 清除本地 Token → 清空 user。
   * 即使后端请求失败，也会继续清除本地状态，确保前端退出登录。
   */
  async function logout() {
    const refresh = getRefreshToken()
    if (refresh) {
      try {
        await authApi.logout(refresh)
      } catch {
        // 后端失败不影响本地登出
      }
    }
    clearTokens()
    user.value = null
  }

  /** 直接更新 user，供外部同步用户信息时使用 */
  function setUser(data: User) {
    user.value = data
  }

  /** 更新个人资料：调后端接口 → 把返回的最新用户信息写回 store */
  async function updateProfile(data: MeUpdatePayload) {
    const updated = await meApi.updateMe(data)
    user.value = updated
    return updated
  }

  /**
   * 应用启动时调用（在路由守卫里触发）。
   * 如果本地有 Token，就尝试恢复登录状态；Token 无效则清除。
   * 无论成功失败，最后都会把 initialized 设为 true，通知路由可以继续判断。
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

  /** 判断当前用户是否为管理员，用于菜单权限、页面访问控制等 */
  const isAdmin = () => user.value?.role === 'admin'

  // 把状态和方法暴露出去，组件通过 useAuthStore() 即可访问
  return { user, initialized, login, logout, fetchUser, setUser, updateProfile, init, isAdmin }
})
