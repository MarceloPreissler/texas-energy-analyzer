import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Allow network access
    port: 5173,
    allowedHosts: [
      'localhost',
      'joann-granulocytic-decanically.ngrok-free.dev',  // Your specific ngrok URL
      '.ngrok-free.dev',  // Allow all ngrok URLs
      '.ngrok.io',
      '.ngrok.app',
    ],
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