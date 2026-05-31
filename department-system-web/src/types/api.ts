/**
 * API 通用类型定义。
 *
 * 后端所有接口统一返回 ApiResponse 格式。
 */

/** 后端统一响应结构 */
export interface ApiResponse<T = unknown> {
  code: number      // 0=成功，非0=错误
  message: string
  data: T
}

/** 分页数据结构 */
export interface PageData<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

/** 分页查询参数 */
export interface PageQuery {
  page?: number
  page_size?: number
}
