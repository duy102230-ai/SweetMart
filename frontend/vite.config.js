import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Khi chạy dev, mọi lời gọi /api được chuyển tiếp sang Backend ASP.NET Core (cổng 5080),
// nhờ vậy Frontend và Backend dùng chung origin, không vướng CORS.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { '/api': process.env.VITE_PROXY_TARGET || 'http://localhost:5080' },
  },
})
