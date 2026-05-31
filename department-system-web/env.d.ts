/// <reference types="vite/client" />

/**
 * Vite 环境变量类型声明。
 * 在 .env.development 等文件中定义的 VITE_ 前缀变量会注入到 import.meta.env。
 */
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string  // 后端 API 基础路径，如 /api/v1
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
