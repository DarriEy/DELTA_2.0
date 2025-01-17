import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // Allow external access to the dev server
    port: 5173, // Specify the port you want Vite to use
    hmr: {
      overlay: true, // Ensure HMR overlay is enabled
    },
  },
  // add the base option to the build configuration
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: undefined,
      },
    },
  },
});