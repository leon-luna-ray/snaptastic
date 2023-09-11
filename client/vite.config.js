import { defineConfig } from 'vite';
import { qwikVite } from '@builder.io/qwik/optimizer';

// https://vitejs.dev/config/
export default defineConfig({
  assetsInclude: ['**/*.svg'],
  plugins: [
    qwikVite({
      csr: true,
    }),
  ],
  build: {
    outDir: '../snaptastic/static/dist',
    rollupOptions: {
      output: {
        entryFileNames: 'index.js',
        assetFileNames: 'index.[ext]',
      },
    },
  },
});
