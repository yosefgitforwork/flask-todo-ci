import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Dev-server config. The proxy forwards /api requests to the Flask backend so
// local development is same-origin in the browser — no CORS to configure.
// (In production nginx does the same job; see frontend/nginx.conf.)
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
})
