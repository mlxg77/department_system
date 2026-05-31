/**
 * 用户相关 TypeScript 类型定义。
 *
 * 与后端 schemas/user.py 中的结构对应，
 * 用于前端组件、Store、API 层的类型约束。
 */

export type UserRole = 'admin' | 'student' | 'dorm_manager'
export type Gender = 'male' | 'female' | 'other'

/** 学生扩展档案 */
export interface StudentProfile {
  student_no: string
  gender?: Gender | null
  college?: string | null
  major?: string | null
  grade?: string | null
  class_name?: string | null
  emergency_contact?: string | null
  emergency_phone?: string | null
}

/** 宿管扩展档案 */
export interface DormManagerProfile {
  employee_no: string
  gender?: Gender | null
  hire_date?: string | null
  remark?: string | null
  managed_buildings?: number[] | null
}

/** 管理员扩展档案 */
export interface AdminProfile {
  admin_level: number
  department?: string | null
}

/** 角色档案联合类型 */
export type UserProfile = StudentProfile | DormManagerProfile | AdminProfile

/** 完整用户信息 */
export interface User {
  id: number
  username: string
  role: UserRole
  real_name: string
  phone?: string | null
  email?: string | null
  avatar_url?: string | null
  status: number
  created_at?: string | null
  profile?: UserProfile | null
}

/** 用户列表项（不含档案详情） */
export interface UserListItem {
  id: number
  username: string
  role: UserRole
  real_name: string
  phone?: string | null
  status: number
  created_at?: string | null
}

/** 登录请求参数 */
export interface LoginPayload {
  username: string
  password: string
}

/** 登录成功返回数据 */
export interface LoginResult {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

/** 创建用户请求体 */
export interface UserCreatePayload {
  role: UserRole
  username: string
  password: string
  real_name: string
  phone?: string | null
  email?: string | null
  profile: Record<string, unknown>
}

/** 更新用户请求体 */
export interface UserUpdatePayload {
  real_name?: string
  phone?: string | null
  email?: string | null
  profile?: Record<string, unknown>
}

/** 更新个人资料请求体 */
export interface MeUpdatePayload {
  phone?: string | null
  email?: string | null
  emergency_contact?: string | null
  emergency_phone?: string | null
  remark?: string | null
}

/** 用户列表查询参数 */
export interface UserListQuery {
  page?: number
  page_size?: number
  role?: UserRole
  status?: number
  keyword?: string
  college?: string
  grade?: string
}
