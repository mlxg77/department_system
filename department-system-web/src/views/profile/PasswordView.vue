<!--
  修改密码页面。

  需输入原密码验证身份，新密码需确认两次一致。
-->
<script setup lang="ts">
import { reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { changePassword } from '@/api/me'

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  old_password: '',
  new_password: '',
  confirm: '',
})

const rules: FormRules = {
  old_password: [{ required: true, message: '请输入原密码' }],
  new_password: [{ required: true, min: 6, max: 32, message: '新密码 6-32 位' }],
  confirm: [
    { required: true, message: '请确认新密码' },
    {
      validator: (_r, value, callback) => {
        if (value !== form.new_password) callback(new Error('两次密码不一致'))
        else callback()
      },
      trigger: 'blur',
    },
  ],
}

async function submit() {
  await formRef.value?.validate()
  loading.value = true
  try {
    await changePassword(form.old_password, form.new_password)
    ElMessage.success('密码已修改，请重新登录')
    form.old_password = ''
    form.new_password = ''
    form.confirm = ''
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <el-card>
    <template #header>修改密码</template>
    <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" style="max-width: 480px">
      <el-form-item label="原密码" prop="old_password">
        <el-input v-model="form.old_password" type="password" show-password />
      </el-form-item>
      <el-form-item label="新密码" prop="new_password">
        <el-input v-model="form.new_password" type="password" show-password />
      </el-form-item>
      <el-form-item label="确认新密码" prop="confirm">
        <el-input v-model="form.confirm" type="password" show-password />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" @click="submit">确认修改</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>
