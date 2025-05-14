<script setup>
import {
  IconApps,
  IconBug,
  IconFile,
  IconStorage,
  IconLink,
  IconCode,
  IconCommand,
} from '@arco-design/web-vue/es/icon';
import {useRouter} from "vue-router";
import {Message} from "@arco-design/web-vue";
import { ref, onMounted, watch } from 'vue';

const router = useRouter();
// 根据当前路由初始化选中的菜单项
const currentRoute = router.currentRoute.value.path;
const initialSelectedKey = getMenuKeyFromRoute(currentRoute);
const selectedKeys = ref([initialSelectedKey]);
const openKeys = ref(['interface']);

// 根据路由路径获取对应的菜单key
function getMenuKeyFromRoute(route) {
  // 处理根路径
  if (route === '/') {
    return 'home';
  }
  
  // 移除开头的斜杠，然后将斜杠替换为连字符
  return route.replace(/^\//, '').replace(/\//g, '-');
}

// 监听路由变化，更新选中的菜单项
watch(() => router.currentRoute.value.path, (newPath) => {
  const menuKey = getMenuKeyFromRoute(newPath);
  if (menuKey && !menuKey.includes('login') && !menuKey.includes('register')) {
    selectedKeys.value = [menuKey];
  }
});

function handleMenuClick(key) {
  selectedKeys.value = [key];
  router.push("/" + key.split("-").join("/"));
}
</script>

<template>
  <div class="menu-container">
    <div class="menu-header">
      <icon-apps class="menu-header-icon" />
      <span class="menu-header-title">功能导航</span>
    </div>
    <a-menu
        class="side-menu"
        :style="{ width: '100%', height: 'calc(100% - 60px)' }"
        @menu-item-click="handleMenuClick"
        :selected-keys="selectedKeys"
        :open-keys="openKeys"
        show-collapse-button
        accordion
    >
      <a-sub-menu key="interface">
        <template #icon>
          <icon-code />
        </template>
        <template #title>接口管理</template>
        <a-menu-item key="interface-manage">
          <template #icon><icon-command /></template>
          命名空间管理
        </a-menu-item>
        <a-menu-item key="interface-chain">
          <template #icon><icon-link /></template>
          任务链管理
        </a-menu-item>
        <a-menu-item key="interface-runtime">
          <template #icon><icon-bug /></template>
          运行结果查看
        </a-menu-item>
        <a-menu-item key="interface-packages">
          <template #icon><icon-apps /></template>
          第三方库依赖
        </a-menu-item>
      </a-sub-menu>
    </a-menu>
  </div>
</template>

<style scoped>
.menu-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.menu-header {
  height: 50px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: linear-gradient(135deg, rgba(0, 57, 230, 0.8) 0%, rgba(23, 43, 77, 0.9) 100%);
  position: relative;
  z-index: 1;
}

.menu-header-icon {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.9);
  margin-right: 10px;
}

.menu-header-title {
  font-size: 15px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  letter-spacing: 0.15px;
}

.side-menu {
  border-right: none;
  background: transparent;
  position: relative;
  z-index: 1;
}

.side-menu :deep(.arco-menu-inner) {
  padding: 8px 0;
}

.side-menu :deep(.arco-menu-item) {
  margin: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s;
  color: rgba(255, 255, 255, 0.8);
  height: 40px;
  line-height: 40px;
}

.side-menu :deep(.arco-menu-selected) {
  background-color: rgba(255, 255, 255, 0.15);
  color: white;
  font-weight: 500;
}

.side-menu :deep(.arco-menu-item:hover:not(.arco-menu-selected)) {
  background-color: rgba(255, 255, 255, 0.08);
  color: white;
}

.side-menu :deep(.arco-menu-icon) {
  margin-right: 12px;
  font-size: 18px;
}

.side-menu :deep(.arco-menu-pop-header) {
  margin-bottom: 4px;
}

.side-menu :deep(.arco-menu-inline-header) {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  letter-spacing: 0.15px;
  height: 48px;
  line-height: 48px;
}

.side-menu :deep(.arco-menu-inline-header:hover) {
  background-color: rgba(255, 255, 255, 0.08);
}

.side-menu :deep(.arco-menu-inline-header.arco-menu-selected) {
  color: white;
}

.side-menu :deep(.arco-menu-collapse-button) {
  color: rgba(255, 255, 255, 0.7);
  background-color: transparent;
  border-radius: 4px;
}

.side-menu :deep(.arco-menu-collapse-button:hover) {
  color: white;
  background-color: rgba(255, 255, 255, 0.08);
}

.side-menu :deep(.arco-icon) {
  transition: all 0.3s;
}

.side-menu :deep(.arco-menu-selected .arco-icon) {
  color: white;
}

/* Material Design ripple effect for menu items */
.side-menu :deep(.arco-menu-item),
.side-menu :deep(.arco-menu-inline-header) {
  position: relative;
  overflow: hidden;
}

.side-menu :deep(.arco-menu-item)::after,
.side-menu :deep(.arco-menu-inline-header)::after {
  content: "";
  display: block;
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  pointer-events: none;
  background-image: radial-gradient(circle, rgba(0, 0, 0, 0.1) 10%, transparent 10.01%);
  background-repeat: no-repeat;
  background-position: 50%;
  transform: scale(10, 10);
  opacity: 0;
  transition: transform 0.5s, opacity 1s;
}

.side-menu :deep(.arco-menu-item:active)::after,
.side-menu :deep(.arco-menu-inline-header:active)::after {
  transform: scale(0, 0);
  opacity: 0.2;
  transition: 0s;
}
</style>
