/**
 * 前端应用入口文件。
 *
 * 负责：
 * 1. 引入全局样式
 * 2. 创建 Vue 应用实例
 * 3. 注册 Pinia（状态管理）、Vue Router（路由）、Element Plus（UI 组件库）
 * 4. 挂载到 index.html 的 #app 元素
 */

import './styles/index.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())                        // 状态管理
app.use(router)                               // 路由
app.use(ElementPlus, { locale: zhCn })        // UI 组件库（中文）

app.mount('#app')
