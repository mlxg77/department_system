<!--
  主布局组件：登录后所有页面的公共框架。

  结构：左侧侧边栏导航 + 顶部 Header + 右侧内容区（router-view）
  管理员可见额外的用户管理菜单项。
-->
<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  HomeFilled,
  User,
  UserFilled,
  Key,
  SwitchButton,
  OfficeBuilding,
  Avatar,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { ROLE_LABELS } from '@/utils/constants'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const activeMenu = computed(() => route.path)

async function handleLogout() {
  await auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="brand">学生公寓管理</div>
      <el-menu :default-active="activeMenu" router>
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/profile">
          <el-icon><User /></el-icon>
          <span>个人资料</span>
        </el-menu-item>
        <el-menu-item index="/profile/password">
          <el-icon><Key /></el-icon>
          <span>修改密码</span>
        </el-menu-item>
        <template v-if="auth.isAdmin()">
          <el-divider class="menu-divider" />
          <el-menu-item index="/admin/users">
            <el-icon><UserFilled /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/students">
            <el-icon><Avatar /></el-icon>
            <span>学生管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/dorm-managers">
            <el-icon><OfficeBuilding /></el-icon>
            <span>宿管管理</span>
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <span class="page-title">{{ route.meta.title }}</span>
        <div class="header-right">
          <span class="user-info">
            {{ auth.user?.real_name }}
            <el-tag size="small" type="info">{{ auth.user ? ROLE_LABELS[auth.user.role] : '' }}</el-tag>
          </span>
          <el-button type="danger" link :icon="SwitchButton" @click="handleLogout">退出</el-button>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout {
  min-height: 100vh;
}
.aside {
  background: #304156;
  color: #fff;
}
.brand {
  height: 56px;
  line-height: 56px;
  text-align: center;
  font-weight: 600;
  font-size: 15px;
  color: #fff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.aside :deep(.el-menu) {
  border-right: none;
  background: transparent;
}
.aside :deep(.el-menu-item) {
  color: #bfcbd9;
}
.aside :deep(.el-menu-item.is-active) {
  color: #409eff;
  background: rgba(64, 158, 255, 0.12);
}
.menu-divider {
  margin: 8px 16px;
  border-color: rgba(255, 255, 255, 0.12);
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
}
.page-title {
  font-size: 16px;
  font-weight: 500;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
}
.main {
  background: #f5f7fa;
}
</style>
