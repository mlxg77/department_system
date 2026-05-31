<!--
  用户新建/编辑弹窗组件。

  新建时可选择角色并填写完整信息（含密码）；
  编辑时只能修改姓名、联系方式和角色档案。
-->
<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import RoleProfileFields from '@/components/user/RoleProfileFields.vue'
import { createUser, getUser, updateUser } from '@/api/users'
import type { User, UserRole } from '@/types/user'
import { ROLE_LABELS } from '@/utils/constants'

const props = defineProps<{
  userId?: number | null
  defaultRole?: UserRole
}>()

const visible = defineModel<boolean>('visible', { default: false })
const emit = defineEmits<{ saved: [] }>()

const formRef = ref<FormInstance>()
const loading = ref(false)
const isEdit = computed(() => props.userId != null)

const form = reactive({
  role: 'student' as UserRole,
  username: '',
  password: '',
  real_name: '',
  phone: '',
  email: '',
  profile: {} as Record<string, unknown>,
})

const rules: FormRules = {
  role: [{ required: true, message: '请选择角色' }],
  username: [{ required: true, min: 3, max: 50, message: '用户名 3-50 位' }],
  password: [{ required: true, min: 6, max: 32, message: '密码 6-32 位' }],
  real_name: [{ required: true, message: '请输入姓名' }],
}

const dialogRules = computed<FormRules>(() => {
  const r = { ...rules }
  if (isEdit.value) {
    delete r.password
    delete r.username
    delete r.role
  }
  return r
})

function defaultProfile(role: UserRole): Record<string, unknown> {
  if (role === 'student') return { student_no: '', gender: undefined, college: '', major: '', grade: '', class_name: '' }
  if (role === 'dorm_manager') return { employee_no: '', gender: undefined, hire_date: '', remark: '' }
  return { admin_level: 1, department: '' }
}

function resetForm() {
  form.role = props.defaultRole ?? 'student'
  form.username = ''
  form.password = ''
  form.real_name = ''
  form.phone = ''
  form.email = ''
  form.profile = defaultProfile(form.role)
}

async function loadUser(id: number) {
  loading.value = true
  try {
    const user: User = await getUser(id)
    form.role = user.role
    form.real_name = user.real_name
    form.phone = user.phone ?? ''
    form.email = user.email ?? ''
    form.profile = { ...(user.profile as unknown as Record<string, unknown>) }
  } finally {
    loading.value = false
  }
}

watch(visible, async (open) => {
  if (!open) return
  if (props.userId) {
    await loadUser(props.userId)
  } else {
    resetForm()
  }
})

watch(
  () => form.role,
  (role, prev) => {
    if (!visible.value || isEdit.value) return
    if (prev && role !== prev) form.profile = defaultProfile(role)
  },
)

async function submit() {
  await formRef.value?.validate()
  loading.value = true
  try {
    if (isEdit.value && props.userId) {
      await updateUser(props.userId, {
        real_name: form.real_name,
        phone: form.phone || null,
        email: form.email || null,
        profile: form.profile,
      })
    } else {
      await createUser({
        role: form.role,
        username: form.username,
        password: form.password,
        real_name: form.real_name,
        phone: form.phone || null,
        email: form.email || null,
        profile: form.profile,
      })
    }
    visible.value = false
    emit('saved')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑用户' : '新建用户'"
    width="560px"
    destroy-on-close
    @closed="formRef?.resetFields()"
  >
    <el-form ref="formRef" v-loading="loading" :model="form" :rules="dialogRules" label-width="100px">
      <el-form-item v-if="!isEdit" label="角色" prop="role">
        <el-select v-model="form.role" :disabled="!!defaultRole">
          <el-option v-for="(label, key) in ROLE_LABELS" :key="key" :label="label" :value="key" />
        </el-select>
      </el-form-item>
      <el-form-item v-if="!isEdit" label="用户名" prop="username">
        <el-input v-model="form.username" placeholder="学号 / 工号 / 登录名" />
      </el-form-item>
      <el-form-item v-if="!isEdit" label="密码" prop="password">
        <el-input v-model="form.password" type="password" show-password />
      </el-form-item>
      <el-form-item label="姓名" prop="real_name">
        <el-input v-model="form.real_name" />
      </el-form-item>
      <el-form-item label="手机">
        <el-input v-model="form.phone" />
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input v-model="form.email" />
      </el-form-item>
      <el-divider content-position="left">{{ ROLE_LABELS[form.role] }}档案</el-divider>
      <RoleProfileFields v-model:profile="form.profile" :role="form.role" :mode="isEdit ? 'edit' : 'create'" />
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="submit">保存</el-button>
    </template>
  </el-dialog>
</template>
