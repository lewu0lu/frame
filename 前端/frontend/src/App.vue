<script setup>
import FuncMenu from "@/menu/FuncMenu.vue";
</script>

<template>
  <main>
    <a-layout class="layout">
      <a-layout-header class="app-header">
        <div class="header-content">
          <div class="logo-container">
            <div class="logo-bg">
              <img alt="Vue logo" src="./assets/logo.svg" width="36" height="36" class="logo-image"/>
            </div>
            <h1 class="app-title">任务管理系统</h1>
          </div>
          <div class="header-actions">
            <a-space>
              <a-avatar :size="32" class="user-avatar">
                <icon-user />
              </a-avatar>
            </a-space>
          </div>
        </div>
      </a-layout-header>
      <a-layout class="main-container">
        <a-layout-sider class="app-sider">
          <FuncMenu/>
        </a-layout-sider>
        <a-layout-content class="app-content">
          <div class="content-wrapper">
            <RouterView/>
          </div>
        </a-layout-content>
      </a-layout>
      <a-layout-footer class="app-footer">
        <div class="footer-content">
          <span>© 2025 任务管理系统 - All Rights Reserved</span>
          <span>Version 1.0.0</span>
        </div>
      </a-layout-footer>
    </a-layout>
  </main>
</template>

<style scoped>
.layout {
  height: 100vh;
  min-height: 100vh;
  background-color: var(--app-bg-secondary);
}

.app-header {
  height: 64px;
  background-color: var(--app-primary);
  padding: 0 20px;
  box-shadow: var(--app-shadow-2);
  position: relative;
  z-index: 10;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-bg {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  background-color: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s;
}

.logo-bg:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

.logo-image {
  width: 32px;
  height: 32px;
}

.app-title {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  color: white;
  letter-spacing: 0.5px;
}

.user-avatar {
  background-color: rgba(255, 255, 255, 0.2);
  transition: background-color 0.3s;
}

.user-avatar:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

.main-container {
  height: calc(100vh - 124px);
}

.app-sider {
  background-color: var(--app-bg-primary);
  border-right: 1px solid var(--app-border-color);
  box-shadow: var(--app-shadow-1);
  position: relative;
  z-index: 5;
}

.app-content {
  padding: 24px;
  overflow: auto;
  background-color: var(--app-bg-secondary);
}

.content-wrapper {
  background-color: var(--app-bg-primary);
  border-radius: 4px;
  padding: 24px;
  min-height: calc(100% - 48px);
  box-shadow: var(--app-shadow-1);
}

.app-footer {
  height: 60px;
  background-color: var(--app-bg-primary);
  border-top: 1px solid var(--app-border-color);
  padding: 0 20px;
  position: relative;
  z-index: 10;
}

.footer-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  color: var(--app-text-secondary);
  font-size: 14px;
}
</style>
