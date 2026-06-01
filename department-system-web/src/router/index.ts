/**
 * Vue Router 路由配置。
 *
 * 路由结构：
 * - /login          登录页（公开，无需 Token）
 * - /               主布局（需登录）
 *   - /dashboard    首页
 *   - /profile      个人资料
 *   - /profile/password  修改密码
 *   - /admin/users  用户管理（仅 admin）
 *   - /admin/students    学生管理（仅 admin）
 *   - /admin/dorm-managers  宿管管理（仅 admin）
 *
 * beforeEach 导航守卫：检查登录状态和角色权限。
 */

import { createRouter, createWebHistory } from 'vue-router'
import { getAccessToken, getRefreshToken } from '@/utils/storage'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({

  // 后退时：浏览器负责「上一个 URL 是什么」，routes 负责「这个 URL 显示谁」，history 负责把两者接起来。
  // routes：地图——/profile 对应哪个 .vue
  // history：交通工具——怎么在浏览器里「记下并恢复」这些路径
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/login/LoginView.vue'),
      meta: { public: true, title: '登录' },  // public=true 表示无需登录
    },
    {
      path: '/',
      component: () => import('@/layouts/MainLayout.vue'),  // 带侧边栏的主布局
      // 当用户只访问根路径 / 时，自动改去 /dashboard，不要停在「空的主布局」上。
      redirect: '/dashboard', 
      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/dashboard/DashboardView.vue'),
          meta: { title: '首页' },
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('@/views/profile/ProfileView.vue'),
          meta: { title: '个人资料' },
        },
        {
          path: 'profile/password',
          name: 'profile-password',
          component: () => import('@/views/profile/PasswordView.vue'),
          meta: { title: '修改密码' },
        },
        {
          path: 'admin/users',
          name: 'admin-users',
          component: () => import('@/views/admin/users/UserListView.vue'),
          meta: { title: '用户管理', roles: ['admin'], listMode: 'all' },
        },
        {
          path: 'admin/students',
          name: 'admin-students',
          component: () => import('@/views/admin/users/UserListView.vue'),
          meta: { title: '学生管理', roles: ['admin'], listMode: 'students' },
        },
        {
          path: 'admin/dorm-managers',
          name: 'admin-dorm-managers',
          component: () => import('@/views/admin/users/UserListView.vue'),
          meta: { title: '宿管管理', roles: ['admin'], listMode: 'dorm-managers' },
        },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/dashboard' },  // 404 重定向到首页
  ],
})

// 全局导航守卫：每次路由跳转前执行
router.beforeEach(async (to, _from, next) => {
  const auth = useAuthStore()

  // 首次访问时初始化认证状态（尝试用 Token 恢复登录）
  if (!auth.initialized) {
    await auth.init()
  }

  // 公开页面（如登录页）：已登录则跳转到首页
  if (to.meta.public) {
    if (getAccessToken() && to.name === 'login') {
      next({ name: 'dashboard' })
      return
    }
    next()
    return
  }

  // 未登录：跳转到登录页，并记录原本要访问的路径
  if (!getAccessToken() && !getRefreshToken()) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }

  // 角色权限检查：路由 meta.roles 限制了允许访问的角色
  const roles = to.meta.roles as string[] | undefined
  if (roles?.length && auth.user && !roles.includes(auth.user.role)) {
    next({ name: 'dashboard' })
    return
  }

  document.title = `${to.meta.title ?? '学生公寓管理'} - 学生公寓管理系统`
  next()
})

export default router
