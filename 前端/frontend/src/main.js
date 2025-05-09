import {createApp} from 'vue'
import App from './App.vue'
import router from './router.js'
import ArcoVue from '@arco-design/web-vue';
import ArcoVueIcon from '@arco-design/web-vue/es/icon';
import '@arco-design/web-vue/dist/arco.css';
import './assets/global.css';

// 移除默认主题
document.body.removeAttribute('arco-theme');

// 创建应用实例
const app = createApp(App);

// 注册全局组件和插件
app.use(router)
   .use(ArcoVue, {
     // Arco Design Vue 配置
     size: 'medium',
     // 可以在这里添加全局配置
   })
   .use(ArcoVueIcon);

// 挂载应用
app.mount('#app');
