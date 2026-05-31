<!--
  角色档案表单字段组件。

  根据 role 属性渲染不同角色的专属字段：
  - student: 学号、学院、专业等
  - dorm_manager: 工号、入职日期等
  - admin: 管理级别、部门
-->
<script setup lang="ts">
import { GENDER_OPTIONS } from '@/utils/constants'
import type { UserRole } from '@/types/user'

defineProps<{
  role: UserRole
  mode: 'create' | 'edit'
}>()

const profile = defineModel<Record<string, unknown>>('profile', { required: true })
</script>

<template>
  <template v-if="role === 'student'">
    <el-form-item v-if="mode === 'create'" label="学号" prop="profile.student_no" :rules="[{ required: true, message: '请输入学号' }]">
      <el-input v-model="profile.student_no" placeholder="学号" />
    </el-form-item>
    <el-form-item label="性别">
      <el-select v-model="profile.gender" clearable placeholder="请选择">
        <el-option v-for="g in GENDER_OPTIONS" :key="g.value" :label="g.label" :value="g.value" />
      </el-select>
    </el-form-item>
    <el-form-item label="学院">
      <el-input v-model="profile.college" />
    </el-form-item>
    <el-form-item label="专业">
      <el-input v-model="profile.major" />
    </el-form-item>
    <el-form-item label="年级">
      <el-input v-model="profile.grade" />
    </el-form-item>
    <el-form-item label="班级">
      <el-input v-model="profile.class_name" />
    </el-form-item>
    <el-form-item v-if="mode === 'create'" label="紧急联系人">
      <el-input v-model="profile.emergency_contact" />
    </el-form-item>
    <el-form-item v-if="mode === 'create'" label="紧急联系电话">
      <el-input v-model="profile.emergency_phone" />
    </el-form-item>
  </template>

  <template v-else-if="role === 'dorm_manager'">
    <el-form-item v-if="mode === 'create'" label="工号" prop="profile.employee_no" :rules="[{ required: true, message: '请输入工号' }]">
      <el-input v-model="profile.employee_no" placeholder="工号" />
    </el-form-item>
    <el-form-item label="性别">
      <el-select v-model="profile.gender" clearable placeholder="请选择">
        <el-option v-for="g in GENDER_OPTIONS" :key="g.value" :label="g.label" :value="g.value" />
      </el-select>
    </el-form-item>
    <el-form-item label="入职日期">
      <el-date-picker
        v-model="profile.hire_date"
        type="date"
        value-format="YYYY-MM-DD"
        placeholder="选择日期"
        style="width: 100%"
      />
    </el-form-item>
    <el-form-item label="备注">
      <el-input v-model="profile.remark" type="textarea" :rows="2" />
    </el-form-item>
  </template>

  <template v-else-if="role === 'admin'">
    <el-form-item label="管理级别">
      <el-input-number v-model="profile.admin_level" :min="1" :max="9" />
    </el-form-item>
    <el-form-item label="所属部门">
      <el-input v-model="profile.department" />
    </el-form-item>
  </template>
</template>
