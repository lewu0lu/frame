import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import {vitePluginForArco} from '@arco-plugins/vite-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vitePluginForArco({
      style: 'css'
    })
  ],
  server: {
    port: 5173,
    proxy: {
      // 代理API请求到后端，但避免代理前端路由
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/user': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/file': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/script': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/task_chain': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/package': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
