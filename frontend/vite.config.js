import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // During local dev, requests to /api/* are forwarded to your backend.
      // Change the target to wherever your backend actually runs.
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
});
