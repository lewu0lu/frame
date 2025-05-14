<script setup>
import { getCurrentUser } from '@/api/user_api';
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const user = ref(getCurrentUser());
const currentTime = ref(new Date());
const timeString = ref('');

// 更新当前时间
onMounted(() => {
  updateTime();
  setInterval(updateTime, 1000);
});

function updateTime() {
  currentTime.value = new Date();
  timeString.value = currentTime.value.toLocaleTimeString();
}

// 获取当前时间的问候语
const getGreeting = () => {
  const hour = currentTime.value.getHours();
  if (hour < 6) return '深夜好';
  if (hour < 12) return '上午好';
  if (hour < 14) return '中午好';
  if (hour < 18) return '下午好';
  return '晚上好';
};

// 导航到功能模块
function navigateTo(path) {
  router.push(path);
}
</script>

<template>
  <div class="welcome-container">
    <div class="welcome-header">
      <h1 class="welcome-title">{{ getGreeting() }}，{{ user?.username || '用户' }}</h1>
      <div class="time-display">{{ timeString }}</div>
    </div>
    
    <p class="welcome-message">欢迎使用任务管理系统，请从左侧功能栏选择需要的功能</p>
    
    <div class="feature-list">
      <div class="feature-item" @click="navigateTo('/interface/manage')">
        <icon-code class="feature-icon" />
        <div class="feature-info">
          <h3>命名空间管理</h3>
          <p>管理您的脚本和接口</p>
        </div>
        <icon-right class="arrow-icon" />
      </div>
      
      <div class="feature-item" @click="navigateTo('/interface/chain')">
        <icon-link class="feature-icon" />
        <div class="feature-info">
          <h3>任务链管理</h3>
          <p>管理您的任务链和工作流</p>
        </div>
        <icon-right class="arrow-icon" />
      </div>
      
      <div class="feature-item" @click="navigateTo('/interface/runtime')">
        <icon-bug class="feature-icon" />
        <div class="feature-info">
          <h3>运行结果查看</h3>
          <p>查看您的脚本运行结果</p>
        </div>
        <icon-right class="arrow-icon" />
      </div>
      
      <div class="feature-item" @click="navigateTo('/interface/packages')">
        <icon-apps class="feature-icon" />
        <div class="feature-info">
          <h3>第三方库依赖</h3>
          <p>管理系统包和依赖</p>
        </div>
        <icon-right class="arrow-icon" />
      </div>
    </div>
    
    <div class="system-status">
      <span>系统版本：1.0.0</span>
      <span class="status-indicator">
        <span class="status-dot"></span>
        正常运行中
      </span>
    </div>
  </div>
</template>

<style scoped>
.welcome-container {
  height: 100%;
  padding: 16px 24px;
  display: flex;
  flex-direction: column;
}

.welcome-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.welcome-title {
  font-size: 22px;
  color: var(--app-text-primary);
  margin: 0;
  background: var(--gradient-blue-royal);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  font-weight: 500;
}

.time-display {
  font-size: 18px;
  color: white;
  background: var(--gradient-blue-soft);
  padding: 6px 14px;
  border-radius: 20px;
  box-shadow: var(--app-shadow-1);
}

.welcome-message {
  font-size: 16px;
  color: var(--app-text-secondary);
  margin-bottom: 32px;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 32px;
  flex: 1; /* Take up available space */
}

.feature-item {
  display: flex;
  align-items: center;
  padding: 20px; /* Increased padding */
  background-color: white;
  border-radius: 8px;
  box-shadow: var(--app-shadow-1);
  transition: all 0.3s;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.04);
  height: calc(20% - 12px); /* Distribute items evenly */
  min-height: 80px; /* Ensure minimum height */
}

.feature-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--app-shadow-primary);
  background: linear-gradient(to right, white, rgba(83, 147, 255, 0.05));
  border-color: rgba(41, 121, 255, 0.1);
}

.feature-icon {
  font-size: 24px; /* Slightly larger */
  color: white;
  margin-right: 16px;
  padding: 12px; /* Larger padding */
  background: var(--gradient-blue-royal);
  border-radius: 6px;
  box-shadow: var(--app-shadow-1);
}

.feature-info {
  flex: 1;
}

.feature-info h3 {
  margin: 0 0 6px 0;
  font-size: 18px; /* Larger font size */
  color: var(--app-text-primary);
}

.feature-info p {
  margin: 0;
  font-size: 14px;
  color: var(--app-text-secondary);
}

.arrow-icon {
  font-size: 18px;
  color: var(--app-text-secondary);
  transition: transform 0.3s;
}

.feature-item:hover .arrow-icon {
  transform: translateX(4px);
  color: var(--app-primary);
}

.system-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--gradient-blue-navy);
  border-radius: 8px;
  box-shadow: var(--app-shadow-1);
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
}

.status-indicator {
  display: flex;
  align-items: center;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #4facfe;
  margin-right: 8px;
  position: relative;
}

.status-dot::after {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background-color: inherit;
  opacity: 0.5;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(2);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 0;
  }
}
</style>
