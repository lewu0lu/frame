<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getCurrentUser, logout, verifyToken } from '@/api/user_api';
import { Message } from '@arco-design/web-vue';

const router = useRouter();
const dropdownVisible = ref(false);
const user = ref(getCurrentUser());

// 计算属性：是否已登录
const isLoggedIn = computed(() => !!user.value);

// 计算属性：用户名首字母（用于头像显示）
const userInitial = computed(() => {
  if (user.value && user.value.username) {
    return user.value.username.charAt(0).toUpperCase();
  }
  return 'U';
});

// 组件挂载时初始化用户状态
onMounted(() => {
  // 初始化用户状态
  updateUserState();
  
  // 监听路由变化，但不处理重定向（让router.js处理）
  router.afterEach(() => {
    // 路由变化后更新用户状态，但不做重定向
    updateUserState();
  });
});

// 简单更新用户状态的函数，不处理认证和重定向
function updateUserState() {
  // 从localStorage获取最新用户信息
  user.value = getCurrentUser();
  console.log("用户状态已更新:", user.value?.username || "未登录");
}

// 处理登出
function handleLogout() {
  logout();
  user.value = null;
  dropdownVisible.value = false;
  
  Message.success({
    content: '已成功登出',
    duration: 2000,
  });
  
  // 重定向到登录页
  router.push('/login');
}

// 处理个人资料
function handleProfile() {
  dropdownVisible.value = false;
  // 这里可以添加跳转到个人资料页的逻辑
  Message.info({
    content: '个人资料功能即将上线',
    duration: 2000,
  });
}

// 处理下拉菜单选择
function handleSelect(key) {
  if (key === 'logout') {
    handleLogout();
  } else if (key === 'profile') {
    handleProfile();
  }
}
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
              <!-- 未登录状态显示登录按钮 -->
              <template v-if="!isLoggedIn">
                <a-button type="outline" @click="router.push('/login')" class="login-button">
                  登录
                </a-button>
                <a-button type="primary" @click="router.push('/register')" class="register-button">
                  注册
                </a-button>
              </template>
              
              <!-- 已登录状态显示用户名、头像和下拉菜单 -->
              <div v-else class="user-container">
                <span class="username-display">{{ user?.username }}</span>
                <a-dropdown trigger="click" @select="handleSelect" v-model:popup-visible="dropdownVisible">
                  <a-avatar :size="36" class="user-avatar">
                    {{ userInitial }}
                  </a-avatar>
                  <template #content>
                    <a-doption value="profile">
                      <template #icon><icon-user /></template>
                      <template #default>个人资料</template>
                    </a-doption>
                    <a-doption value="logout">
                      <template #icon><icon-export /></template>
                      <template #default>退出登录</template>
                    </a-doption>
                  </template>
                </a-dropdown>
              </div>
            </a-space>
          </div>
        </div>
      </a-layout-header>
      
      <!-- 主要内容区域 -->
      <a-layout class="main-container">
        <!-- 内容区域 -->
        <a-layout-content class="app-content" :class="{ 'full-width': !isLoggedIn }">
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
  height: 60px;
  background: var(--gradient-blue-royal);
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
  width: 36px;
  height: 36px;
  border-radius: 6px;
  background-color: rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s;
}

.logo-bg:hover {
  background-color: rgba(255, 255, 255, 0.25);
}

.logo-image {
  width: 28px;
  height: 28px;
}

.app-title {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: white;
  letter-spacing: 0.5px;
}

.user-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.username-display {
  color: white;
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 0.5px;
  opacity: 0.9;
  transition: all 0.3s;
}

.user-container:hover .username-display {
  opacity: 1;
}

.user-avatar {
  background-color: rgba(255, 255, 255, 0.2);
  transition: all 0.3s;
  cursor: pointer;
  color: white;
  font-weight: 500;
}

.user-avatar:hover {
  background-color: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.login-button, .register-button {
  height: 36px;
  transition: all 0.3s;
}

.login-button {
  color: white;
  border-color: rgba(255, 255, 255, 0.5);
}

.login-button:hover, .register-button:hover {
  transform: translateY(-2px);
  box-shadow: var(--app-shadow-1);
}

.main-container {
  height: calc(100vh - 110px); /* Reduced from 124px to 110px (60px header + 50px footer) */
  display: flex;
  flex-direction: column;
}

.app-sider {
  background-color: var(--app-bg-primary);
  border-right: 1px solid var(--app-border-color);
  box-shadow: var(--app-shadow-1);
  position: relative;
  z-index: 5;
}

.app-content {
  padding: 0; /* Remove padding to maximize space */
  overflow: auto;
  background-color: var(--app-bg-secondary);
  flex: 1; /* Take all available space */
}

.app-content.full-width {
  padding: 0;
}

.content-wrapper {
  background-color: var(--app-bg-primary);
  border-radius: 0; /* Remove border radius for full-screen feel */
  padding: 0; /* Remove padding */
  height: 100%; /* Use full height */
  min-height: 100%;
  box-shadow: none; /* Remove shadow for a cleaner look */
}

/* 登录和注册页面不需要内容包装器的样式 */
.app-content.full-width .content-wrapper {
  background-color: transparent;
  box-shadow: none;
  padding: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100%;
  background-image: var(--gradient-tech);
  position: relative;
  overflow: hidden;
}

/* 添加科技风格背景效果 */
.app-content.full-width .content-wrapper::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 10% 10%, rgba(51, 112, 255, 0.1) 0%, transparent 20%),
    radial-gradient(circle at 90% 30%, rgba(103, 58, 183, 0.1) 0%, transparent 20%),
    radial-gradient(circle at 50% 80%, rgba(0, 188, 212, 0.1) 0%, transparent 30%);
  z-index: -1;
}

.app-footer {
  height: 50px;
  background: var(--gradient-blue-navy);
  padding: 0 20px;
  position: relative;
  z-index: 10;
}

.footer-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
}
</style>
