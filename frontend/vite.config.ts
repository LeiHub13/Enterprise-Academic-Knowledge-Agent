import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 开发环境通过 Vite 代理把 /api 转发到 FastAPI（http://localhost:8000）
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
