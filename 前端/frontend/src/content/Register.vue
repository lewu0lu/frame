<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { register } from '@/api/user_api';
import { Message } from '@arco-design/web-vue';

const router = useRouter();
const loading = ref(false);

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
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
  confirmPassword: [
    { required: true, message: '请确认密码' },
    {
      validator: (value, callback) => {
        if (value !== registerForm.password) {
          callback('两次输入的密码不一致');
        }
      },
    },
  ],
};

async function handleSubmit() {
  try {
    loading.value = true;
    
    // 调用注册API
    await register({
      username: registerForm.username,
      password: registerForm.password,
    });
    
    // 注册成功提示
    Message.success({
      content: '注册成功',
      duration: 2000,
    });
    
    // 跳转到首页
    router.push('/home');
  } catch (error) {
    // 注册失败提示
    Message.error({
      content: error.message || '注册失败，请重试',
      duration: 3000,
    });
  } finally {
    loading.value = false;
  }
}

function goToLogin() {
  router.push('/login');
}
</script>

<template>
  <div class="register-container">
    <div class="register-card md-elevation-3">
      <div class="register-header">
        <h2 class="register-title">注册</h2>
        <p class="register-subtitle">创建新账号</p>
      </div>
      
      <a-form 
        :model="registerForm" 
        :rules="rules"
        @submit="handleSubmit"
        layout="vertical"
        class="register-form"
      >
        <a-form-item field="username" label="用户名">
          <a-input 
            v-model="registerForm.username" 
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
            v-model="registerForm.password" 
            placeholder="请输入密码"
            allow-clear
          >
            <template #prefix>
              <icon-lock />
            </template>
          </a-input-password>
        </a-form-item>
        
        <a-form-item field="confirmPassword" label="确认密码">
          <a-input-password 
            v-model="registerForm.confirmPassword" 
            placeholder="请再次输入密码"
            allow-clear
          >
            <template #prefix>
              <icon-check-circle />
            </template>
          </a-input-password>
        </a-form-item>
        
        <div class="register-actions">
          <a-button 
            type="primary" 
            html-type="submit" 
            long 
            :loading="loading"
            class="register-button"
          >
            注册
          </a-button>
        </div>
      </a-form>
      
      <div class="register-footer">
        <p>已有账号？ <a @click="goToLogin">立即登录</a></p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100%;
  padding: var(--app-spacing-lg);
}

.register-card {
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

.register-card:hover {
  box-shadow: var(--app-shadow-2), 0 8px 35px rgba(41, 121, 255, 0.15);
}

/* 添加简约风格顶部渐变边框 */
.register-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--gradient-blue-royal);
  border-radius: 2px 2px 0 0;
}

.register-header {
  text-align: center;
  margin-bottom: var(--app-spacing-lg);
}

.register-title {
  font-size: 24px;
  margin-bottom: var(--app-spacing-xs);
  background: var(--gradient-blue-royal);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.register-subtitle {
  font-size: 14px;
  color: var(--app-text-secondary);
  margin: 0;
}

.register-form {
  margin-bottom: var(--app-spacing-lg);
}

.register-actions {
  margin-top: var(--app-spacing-lg);
}

.register-button {
  height: 44px;
  font-size: 15px;
  position: relative;
  overflow: hidden;
  background: var(--gradient-blue-royal);
  border: none;
  font-weight: 500;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
  border-radius: 22px;
}

.register-button:hover {
  background: var(--gradient-blue-tech);
  box-shadow: var(--app-shadow-primary);
  transform: translateY(-2px);
}

.register-button::after {
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

.register-button:active::after {
  transform: scale(0, 0);
  opacity: 0.2;
  transition: 0s;
}

.register-footer {
  text-align: center;
  font-size: 14px;
  color: var(--app-text-secondary);
}

.register-footer a {
  color: var(--app-primary);
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
  padding: 2px 5px;
  border-radius: 4px;
  position: relative;
}

.register-footer a:hover {
  color: var(--app-primary-light);
  text-decoration: none;
  background-color: rgba(41, 121, 255, 0.08);
}

.register-footer a::after {
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

.register-footer a:hover::after {
  transform: scaleX(1);
  transform-origin: left;
}
</style>
