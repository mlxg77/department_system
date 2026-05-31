<!--
  首页 / 仪表盘。

  展示当前登录用户的基本信息和角色档案（学生学籍、宿管信息、管理员信息）。
-->
<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { GENDER_OPTIONS, ROLE_LABELS } from '@/utils/constants'
import type { AdminProfile, DormManagerProfile, StudentProfile } from '@/types/user'

const auth = useAuthStore()
const user = computed(() => auth.user)

const genderLabel = (value?: string | null) =>
  GENDER_OPTIONS.find((g) => g.value === value)?.label ?? '-'

const studentProfile = computed(() => user.value?.profile as StudentProfile | undefined)
const dormProfile = computed(() => user.value?.profile as DormManagerProfile | undefined)
const adminProfile = computed(() => user.value?.profile as AdminProfile | undefined)
</script>

<template>
  <el-card v-if="user">
    <template #header>欢迎，{{ user.real_name }}</template>
    <el-descriptions :column="2" border>
      <el-descriptions-item label="用户名">{{ user.username }}</el-descriptions-item>
      <el-descriptions-item label="角色">{{ ROLE_LABELS[user.role] }}</el-descriptions-item>
      <el-descriptions-item label="手机">{{ user.phone || '-' }}</el-descriptions-item>
      <el-descriptions-item label="邮箱">{{ user.email || '-' }}</el-descriptions-item>
      <el-descriptions-item label="状态">
        <el-tag :type="user.status === 1 ? 'success' : 'danger'">
          {{ user.status === 1 ? '正常' : '禁用' }}
        </el-tag>
      </el-descriptions-item>
    </el-descriptions>

    <template v-if="user.role === 'student' && studentProfile">
      <el-divider />
      <el-descriptions title="学籍信息" :column="2" border>
        <el-descriptions-item label="学号">{{ studentProfile.student_no }}</el-descriptions-item>
        <el-descriptions-item label="性别">{{ genderLabel(studentProfile.gender) }}</el-descriptions-item>
        <el-descriptions-item label="学院">{{ studentProfile.college || '-' }}</el-descriptions-item>
        <el-descriptions-item label="专业">{{ studentProfile.major || '-' }}</el-descriptions-item>
        <el-descriptions-item label="年级">{{ studentProfile.grade || '-' }}</el-descriptions-item>
        <el-descriptions-item label="班级">{{ studentProfile.class_name || '-' }}</el-descriptions-item>
      </el-descriptions>
    </template>

    <template v-if="user.role === 'dorm_manager' && dormProfile">
      <el-divider />
      <el-descriptions title="宿管信息" :column="2" border>
        <el-descriptions-item label="工号">{{ dormProfile.employee_no }}</el-descriptions-item>
        <el-descriptions-item label="性别">{{ genderLabel(dormProfile.gender) }}</el-descriptions-item>
        <el-descriptions-item label="入职日期">{{ dormProfile.hire_date || '-' }}</el-descriptions-item>
      </el-descriptions>
    </template>

    <template v-if="user.role === 'admin' && adminProfile">
      <el-divider />
      <el-descriptions title="管理员信息" :column="2" border>
        <el-descriptions-item label="管理级别">{{ adminProfile.admin_level }}</el-descriptions-item>
        <el-descriptions-item label="部门">{{ adminProfile.department || '-' }}</el-descriptions-item>
      </el-descriptions>
    </template>
  </el-card>
</template>
