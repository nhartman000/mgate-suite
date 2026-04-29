import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-oxc'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
        changeOrigin: true
      },
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
