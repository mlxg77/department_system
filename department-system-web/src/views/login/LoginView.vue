<!--
  登录页面。

  用户输入用户名和密码，调用 authStore.login() 完成登录，
  成功后跳转到 redirect 参数指定的页面（默认首页）。
-->
<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { Lock, User } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function onSubmit() {
  await formRef.value?.validate()
  loading.value = true
  try {
    await auth.login(form)
    const redirect = (route.query.redirect as string) || '/dashboard'
    router.push(redirect)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <el-card class="login-card" shadow="hover">
      <template #header>
        <h2 class="title">学生公寓管理系统</h2>
        <p class="subtitle">用户登录</p>
      </template>
      <el-form ref="formRef" :model="form" :rules="rules" size="large" @submit.prevent="onSubmit">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名 / 学号 / 工号" prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="onSubmit"
          />
        </el-form-item>
        <el-button type="primary" class="submit-btn" :loading="loading" @click="onSubmit">登 录</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1d3557 0%, #457b9d 50%, #a8dadc 100%);
}
.login-card {
  width: 400px;
}
.title {
  margin: 0;
  text-align: center;
  font-size: 22px;
  color: #303133;
}
.subtitle {
  margin: 8px 0 0;
  text-align: center;
  color: #909399;
  font-size: 14px;
}
.submit-btn {
  width: 100%;
}
</style>
