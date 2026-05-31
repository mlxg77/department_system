<!--
  个人资料编辑页。

  用户可修改手机、邮箱；
  学生还可修改紧急联系人，宿管可修改备注。
  用户名和姓名不可修改。
-->
<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import type { FormInstance } from 'element-plus'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import type { MeUpdatePayload, User } from '@/types/user'

const auth = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  phone: '',
  email: '',
  emergency_contact: '',
  emergency_phone: '',
  remark: '',
})

function applyUserToForm(u: User) {
  form.phone = u.phone ?? ''
  form.email = u.email ?? ''
  const p = u.profile as Record<string, string> | undefined
  form.emergency_contact = p?.emergency_contact ?? ''
  form.emergency_phone = p?.emergency_phone ?? ''
  form.remark = p?.remark ?? ''
}

function resetForm() {
  form.phone = ''
  form.email = ''
  form.emergency_contact = ''
  form.emergency_phone = ''
  form.remark = ''
  formRef.value?.resetFields()
}

onMounted(async () => {
  if (!auth.user) await auth.fetchUser()
  if (auth.user) applyUserToForm(auth.user)
})

async function submit() {
  loading.value = true
  try {
    const payload: MeUpdatePayload = {
      phone: form.phone.trim() || null,
      email: form.email.trim() || null,
    }
    if (auth.user?.role === 'student') {
      payload.emergency_contact = form.emergency_contact.trim() || null
      payload.emergency_phone = form.emergency_phone.trim() || null
    }
    if (auth.user?.role === 'dorm_manager') {
      payload.remark = form.remark.trim() || null
    }
    await auth.updateProfile(payload)
    resetForm()
    ElMessage.success('资料已更新')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <el-card>
    <template #header>编辑个人资料</template>
    <el-form ref="formRef" :model="form" label-width="120px" style="max-width: 520px">
      <el-form-item label="用户名">
        <el-input :model-value="auth.user?.username" disabled />
      </el-form-item>
      <el-form-item label="姓名">
        <el-input :model-value="auth.user?.real_name" disabled />
      </el-form-item>
      <el-form-item label="手机">
        <el-input v-model="form.phone" />
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input v-model="form.email" />
      </el-form-item>
      <template v-if="auth.user?.role === 'student'">
        <el-form-item label="紧急联系人">
          <el-input v-model="form.emergency_contact" />
        </el-form-item>
        <el-form-item label="紧急联系电话">
          <el-input v-model="form.emergency_phone" />
        </el-form-item>
      </template>
      <template v-if="auth.user?.role === 'dorm_manager'">
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" />
        </el-form-item>
      </template>
      <el-form-item>
        <el-button type="primary" :loading="loading" @click="submit">保存</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>
