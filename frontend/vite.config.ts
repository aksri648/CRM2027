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
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  preview: {
    // Render serves the built app via `vite preview`, which rejects unknown
    // Host headers by default. Allow the Render hostname (and any *.onrender.com
    // subdomain so renames or PR previews keep working).
    allowedHosts: ['xeno-crm-2027-frontend.onrender.com', '.onrender.com'],
  },
})