import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    // 1. 允许通过 IP 访问（Docker 或内网测试必备）
    host: '0.0.0.0',
    port: 5173,
    // 2. 配置开发服务器代理，解决跨域问题
    proxy: {
      '/api': {
        // 这里的 localhost:8000 对应你的 FastAPI 后端
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        // 如果你的 FastAPI 路由本身不带 /api 前缀（例如后端是 @app.get("/upload")）
        // 则需要下面这一行将请求中的 /api 抹去后再转给后端
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})