import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: true, // 允许通过 127.0.0.1 / 本机 IP 访问
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': 'http://127.0.0.1:5002'
    }
  }
})

