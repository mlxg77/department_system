/**
 * Vite 构建工具配置。
 *
 * - plugins: Vue 支持 + Vue DevTools
 * - resolve.alias: @ 指向 src 目录，方便 import
 * - server.proxy: 开发时将 /api 请求代理到后端 FastAPI (localhost:8000)
 */

import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',  // 后端 API 地址
        changeOrigin: true,
      },
    },
  },
})
