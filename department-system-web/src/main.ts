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

const app = createApp(App) // 根组件里有 <router-view />
// use(插件)：把插件提供的全局能力挂到整个应用上，之后所有组件都能用。
app.use(createPinia())
app.use(router) // 注册路由
app.use(ElementPlus, { locale: zhCn })
// 把前面创建并配置好的 Vue 应用，真正渲染到页面里那个空的挂载点上
// 挂载到 index.html 的 #app 元素。
app.mount('#app')
