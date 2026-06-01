<!--
  根组件：整个应用的最外层容器。
  router-view 会根据当前 URL 渲染对应的页面组件。
-->
<template>
  <!-- Vue Router 提供的占位组件：当前 URL 匹配到哪个路由，就在这里渲染哪个页面组件 -->
  <router-view />
</template>
