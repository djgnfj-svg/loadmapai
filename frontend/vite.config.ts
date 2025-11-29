import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api/v1/stream': {
        target: 'http://backend:8000',
        changeOrigin: true,
        // SSE 스트리밍에 필수 설정
        configure: (proxy) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // SSE 요청 타임아웃 비활성화
            res.setTimeout(0);
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            // SSE 응답 헤더 설정 - 버퍼링 비활성화
            proxyRes.headers['cache-control'] = 'no-cache';
            proxyRes.headers['x-accel-buffering'] = 'no';
          });
        },
      },
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
    },
  },
})
