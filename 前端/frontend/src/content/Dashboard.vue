<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import FuncMenu from "@/menu/FuncMenu.vue";

const router = useRouter();
const route = useRoute();
const collapsed = ref(false);

// Get the current menu item based on the route
const getPageTitle = () => {
  const path = route.path;
  if (path.includes('interface/manage')) {
    return '命名空间管理';
  } else if (path.includes('interface/chain')) {
    return '任务链管理';
  } else if (path.includes('interface/runtime')) {
    return '运行结果查看';
  } else if (path.includes('interface/packages')) {
    return '第三方库依赖';
  } else {
    return '欢迎使用';
  }
};
</script>

<template>
  <div class="dashboard-container">
    <!-- Left sidebar with menu -->
    <div class="sidebar" :class="{ 'sidebar-collapsed': collapsed }">
      <FuncMenu />
    </div>
    
    <!-- Right content area -->
    <div class="content-area" :class="{ 'content-expanded': collapsed }">
      <div class="content-header">
        <a-breadcrumb class="breadcrumb">
          <a-breadcrumb-item>首页</a-breadcrumb-item>
          <a-breadcrumb-item>{{ getPageTitle() }}</a-breadcrumb-item>
        </a-breadcrumb>
        
        <a-button 
          type="text" 
          class="collapse-btn"
          @click="collapsed = !collapsed"
        >
          <icon-menu-fold v-if="!collapsed" />
          <icon-menu-unfold v-else />
        </a-button>
      </div>
      
      <div class="content-body">
        <RouterView />
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-container {
  display: flex;
  height: 100vh; /* Use viewport height to take full screen height */
  width: 100%;
  position: relative;
  background-color: var(--app-bg-secondary);
  overflow: hidden; /* Prevent scrolling on the container level */
}

.sidebar {
  width: 240px;
  height: 100%;
  transition: width 0.3s ease;
  background: var(--gradient-blue-navy);
  box-shadow: var(--app-shadow-2);
  z-index: 10;
}

.sidebar-collapsed {
  width: 70px;
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s ease;
  overflow: hidden;
}

.content-header {
  height: 48px; /* Reduced height to save vertical space */
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  background-color: var(--app-bg-primary);
  box-shadow: var(--app-shadow-1);
  min-height: 48px; /* Ensure minimum height */
}

.breadcrumb {
  font-size: 14px;
}

.collapse-btn {
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  transition: all 0.3s;
  color: var(--app-primary);
}

.collapse-btn:hover {
  background-color: rgba(41, 121, 255, 0.1);
  color: var(--app-primary-light);
}

.content-body {
  flex: 1;
  padding: 8px; /* Reduced padding to maximize content area */
  overflow: auto;
  background-color: var(--app-bg-secondary);
  display: flex;
  flex-direction: column;
  height: calc(100vh - 48px); /* Full height minus header */
}
</style>
