import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Allow network access
    port: 5173,
    proxy: {
      '/plans': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/plans/providers': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});