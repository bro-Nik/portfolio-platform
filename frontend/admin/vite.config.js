import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  base: '/admin/',
  plugins: [react()],
  resolve: {
    alias: {
      src: fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  build: {
    outDir: 'build',
  },
  optimizeDeps: {
    exclude: ['@portfolio/shared'],
  },
  server: {
    port: 3000,
    host: true,
    watch: {
      usePolling: process.env.VITE_USE_POLLING === 'true',
      interval: 300,
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/setupTests.js',
  },
});
