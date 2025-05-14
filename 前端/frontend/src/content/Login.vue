<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { login } from '@/api/user_api';
import { Message } from '@arco-design/web-vue';

const router = useRouter();
const loading = ref(false);

const loginForm = reactive({
  username: '',
  password: '',
});

const rules = {
  username: [
    { required: true, message: '请输入用户名' },
    { minLength: 3, message: '用户名长度不能小于3个字符' },
  ],
  password: [
    { required: true, message: '请输入密码' },
    { minLength: 6, message: '密码长度不能小于6个字符' },
  ],
};

async function handleSubmit() {
  try {
    loading.value = true;
    
    // 调用登录API
    await login(loginForm);
    
    // 登录成功提示
    Message.success({
      content: '登录成功',
      duration: 2000,
    });
    
    // 跳转到首页
    router.push('/home');
  } catch (error) {
    // 登录失败提示
    Message.error({
      content: error.message || '登录失败，请重试',
      duration: 3000,
    });
  } finally {
    loading.value = false;
  }
}

function goToRegister() {
  router.push('/register');
}
</script>

<template>
  <div class="login-container">
    <div class="login-card md-elevation-3">
      <div class="login-header">
        <h2 class="login-title">登录</h2>
        <p class="login-subtitle">登录到任务管理系统</p>
      </div>
      
      <a-form 
        :model="loginForm" 
        :rules="rules"
        @submit="handleSubmit"
        layout="vertical"
        class="login-form"
      >
        <a-form-item field="username" label="用户名">
          <a-input 
            v-model="loginForm.username" 
            placeholder="请输入用户名"
            allow-clear
          >
            <template #prefix>
              <icon-user />
            </template>
          </a-input>
        </a-form-item>
        
        <a-form-item field="password" label="密码">
          <a-input-password 
            v-model="loginForm.password" 
            placeholder="请输入密码"
            allow-clear
          >
            <template #prefix>
              <icon-lock />
            </template>
          </a-input-password>
        </a-form-item>
        
        <div class="login-actions">
          <a-button 
            type="primary" 
            html-type="submit" 
            long 
            :loading="loading"
            class="login-button"
          >
            登录
          </a-button>
        </div>
      </a-form>
      
      <div class="login-footer">
        <p>还没有账号？ <a @click="goToRegister">立即注册</a></p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100%;
  padding: var(--app-spacing-lg);
}

.login-card {
  width: 100%;
  max-width: 380px;
  background-color: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(15px);
  border-radius: 10px;
  padding: 28px;
  box-shadow: var(--app-shadow-1), 0 5px 30px rgba(41, 121, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.5);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.login-card:hover {
  box-shadow: var(--app-shadow-2), 0 8px 35px rgba(41, 121, 255, 0.15);
}

/* 添加简约风格顶部渐变边框 */
.login-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--gradient-blue-soft);
  border-radius: 2px 2px 0 0;
}

.login-header {
  text-align: center;
  margin-bottom: var(--app-spacing-lg);
}

.login-title {
  font-size: 24px;
  margin-bottom: var(--app-spacing-xs);
  background: var(--gradient-blue-royal);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.login-subtitle {
  font-size: 14px;
  color: var(--app-text-secondary);
  margin: 0;
}

.login-form {
  margin-bottom: var(--app-spacing-lg);
}

.login-actions {
  margin-top: var(--app-spacing-lg);
}

.login-button {
  height: 44px;
  font-size: 15px;
  position: relative;
  overflow: hidden;
  background: var(--gradient-blue-soft);
  border: none;
  font-weight: 500;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
  border-radius: 22px;
}

.login-button:hover {
  background: var(--gradient-blue-royal);
  box-shadow: var(--app-shadow-primary);
  transform: translateY(-2px);
}

.login-button::after {
  content: "";
  display: block;
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  pointer-events: none;
  background-image: radial-gradient(circle, rgba(255, 255, 255, 0.3) 10%, transparent 10.01%);
  background-repeat: no-repeat;
  background-position: 50%;
  transform: scale(10, 10);
  opacity: 0;
  transition: transform 0.5s, opacity 1s;
}

.login-button:active::after {
  transform: scale(0, 0);
  opacity: 0.2;
  transition: 0s;
}

.login-footer {
  text-align: center;
  font-size: 14px;
  color: var(--app-text-secondary);
}

.login-footer a {
  color: var(--app-primary);
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
  padding: 2px 5px;
  border-radius: 4px;
  position: relative;
}

.login-footer a:hover {
  color: var(--app-primary-light);
  text-decoration: none;
  background-color: rgba(41, 121, 255, 0.08);
}

.login-footer a::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 1px;
  background: var(--gradient-blue-soft);
  transform: scaleX(0);
  transition: transform 0.3s ease;
  transform-origin: right;
}

.login-footer a:hover::after {
  transform: scaleX(1);
  transform-origin: left;
}
</style>
