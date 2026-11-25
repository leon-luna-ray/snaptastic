import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

// The backend (port 8080) serves the built `dist/` folder in the kiosk.
// In development, the Vite dev server forwards API and photo requests to it.
// Inside Docker, docker-compose.yml points this at the host machine.
const backend = process.env.SNAPTASTIC_BACKEND || 'http://127.0.0.1:8080';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: 'dist',
  },
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/api': backend,
      '/photos': backend,
    },
  },
});
