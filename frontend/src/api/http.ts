import axios from 'axios'

// 开发期走 Vite 代理（见 vite.config.ts）；生产部署时改为后端实际地址
export const http = axios.create({
  baseURL: '/api',
  timeout: 120_000,
})
