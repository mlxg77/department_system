<!--
  用户列表管理页（管理员专用）。

  通过路由 meta.listMode 区分三种模式：
  - all: 全部用户
  - students: 仅学生
  - dorm-managers: 仅宿管

  功能：搜索筛选、分页、新建/编辑/禁用/删除/重置密码。
-->
<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Search } from '@element-plus/icons-vue'
import UserFormDialog from '@/components/user/UserFormDialog.vue'
import {
  deleteUser,
  listDormManagers,
  listStudents,
  listUsers,
  resetUserPassword,
  updateUserStatus,
} from '@/api/users'
import type { UserListItem, UserRole } from '@/types/user'
import { ROLE_LABELS, STATUS_OPTIONS } from '@/utils/constants'

type ListMode = 'all' | 'students' | 'dorm-managers'

const route = useRoute()
const listMode = computed(() => (route.meta.listMode as ListMode) ?? 'all')

const loading = ref(false)
const tableData = ref<UserListItem[]>([])
const total = ref(0)

const query = reactive({
  page: 1,
  page_size: 20,
  role: undefined as UserRole | undefined,
  status: undefined as number | undefined,
  keyword: '',
  college: '',
  grade: '',
})

const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const defaultRole = computed<UserRole | undefined>(() => {
  if (listMode.value === 'students') return 'student'
  if (listMode.value === 'dorm-managers') return 'dorm_manager'
  return undefined
})

const showRoleFilter = computed(() => listMode.value === 'all')
const showStudentFilters = computed(() => listMode.value === 'students' || query.role === 'student')

async function fetchList() {
  loading.value = true
  try {
    const params = {
      page: query.page,
      page_size: query.page_size,
      status: query.status,
      keyword: query.keyword || undefined,
      college: query.college || undefined,
      grade: query.grade || undefined,
      role: listMode.value === 'all' ? query.role : undefined,
    }
    let result
    if (listMode.value === 'students') result = await listStudents(params)
    else if (listMode.value === 'dorm-managers') result = await listDormManagers(params)
    else result = await listUsers(params)
    tableData.value = result.items
    total.value = result.total
  } finally {
    loading.value = false
  }
}

function onSearch() {
  query.page = 1
  fetchList()
}

function openCreate() {
  editingId.value = null
  dialogVisible.value = true
}

function openEdit(row: UserListItem) {
  editingId.value = row.id
  dialogVisible.value = true
}

async function toggleStatus(row: UserListItem) {
  const next = row.status === 1 ? 0 : 1
  const action = next === 0 ? '禁用' : '启用'
  await ElMessageBox.confirm(`确定要${action}用户「${row.real_name}」吗？`, '提示', { type: 'warning' })
  await updateUserStatus(row.id, next as 0 | 1)
  ElMessage.success(`${action}成功`)
  fetchList()
}

async function handleDelete(row: UserListItem) {
  await ElMessageBox.confirm(`确定删除用户「${row.real_name}」吗？此操作为软删除。`, '警告', {
    type: 'warning',
  })
  await deleteUser(row.id)
  ElMessage.success('已删除')
  fetchList()
}

async function handleResetPassword(row: UserListItem) {
  const { value } = await ElMessageBox.prompt('请输入新密码（6-32 位）', '重置密码', {
    inputPattern: /^.{6,32}$/,
    inputErrorMessage: '密码长度 6-32 位',
  })
  await resetUserPassword(row.id, value)
  ElMessage.success('密码已重置')
}

onMounted(fetchList)
</script>

<template>
  <el-card>
    <el-form :inline="true" class="filter-form" @submit.prevent="onSearch">
      <el-form-item label="关键词">
        <el-input v-model="query.keyword" placeholder="用户名/姓名/手机" clearable style="width: 180px" />
      </el-form-item>
      <el-form-item v-if="showRoleFilter" label="角色">
        <el-select v-model="query.role" clearable placeholder="全部" style="width: 120px">
          <el-option v-for="(label, key) in ROLE_LABELS" :key="key" :label="label" :value="key" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="query.status" clearable placeholder="全部" style="width: 100px">
          <el-option v-for="s in STATUS_OPTIONS" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
      </el-form-item>
      <template v-if="showStudentFilters">
        <el-form-item label="学院">
          <el-input v-model="query.college" clearable style="width: 140px" />
        </el-form-item>
        <el-form-item label="年级">
          <el-input v-model="query.grade" clearable style="width: 100px" />
        </el-form-item>
      </template>
      <el-form-item>
        <el-button type="primary" :icon="Search" @click="onSearch">查询</el-button>
        <el-button :icon="Refresh" @click="fetchList">刷新</el-button>
        <el-button type="success" :icon="Plus" @click="openCreate">新建</el-button>
      </el-form-item>
    </el-form>

    <el-table v-loading="loading" :data="tableData" stripe border>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="username" label="用户名" min-width="120" />
      <el-table-column prop="real_name" label="姓名" min-width="100" />
      <el-table-column label="角色" width="90">
        <template #default="{ row }">{{ ROLE_LABELS[row.role as UserRole] }}</template>
      </el-table-column>
      <el-table-column prop="phone" label="手机" min-width="120" />
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">
            {{ row.status === 1 ? '正常' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" min-width="170" />
      <el-table-column label="操作" fixed="right" width="280">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link :type="row.status === 1 ? 'warning' : 'success'" @click="toggleStatus(row)">
            {{ row.status === 1 ? '禁用' : '启用' }}
          </el-button>
          <el-button link type="primary" @click="handleResetPassword(row)">重置密码</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        background
        @current-change="fetchList"
        @size-change="onSearch"
      />
    </div>

    <UserFormDialog
      v-model:visible="dialogVisible"
      :user-id="editingId"
      :default-role="defaultRole"
      @saved="fetchList"
    />
  </el-card>
</template>

<style scoped>
.filter-form {
  margin-bottom: 16px;
}
.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
