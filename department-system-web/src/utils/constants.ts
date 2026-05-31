/**
 * 全局常量定义。
 *
 * 包含角色标签、性别选项、状态选项、API 错误码映射等。
 */

import type { Gender, UserRole } from '@/types/user'

/** 角色中文名称映射 */
export const ROLE_LABELS: Record<UserRole, string> = {
  admin: '管理员',
  student: '学生',
  dorm_manager: '宿管',
}

/** 性别下拉选项 */
export const GENDER_OPTIONS: { label: string; value: Gender }[] = [
  { label: '男', value: 'male' },
  { label: '女', value: 'female' },
  { label: '其他', value: 'other' },
]

/** 用户状态下拉选项 */
export const STATUS_OPTIONS = [
  { label: '正常', value: 1 },
  { label: '禁用', value: 0 },
]

/** 后端业务错误码 → 中文提示映射 */
export const API_ERROR_MESSAGES: Record<number, string> = {
  40001: '参数校验失败',
  40101: '未登录或登录已过期',
  40301: '无权限访问',
  40401: '资源不存在',
  40901: '用户名或学号/工号已存在',
  50001: '服务器内部错误',
}
