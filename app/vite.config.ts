import { defineConfig } from 'vite';
import preact from '@preact/preset-vite';
import { VitePWA } from 'vite-plugin-pwa';

// base: относительный путь, чтобы приложение работало на GitHub Pages в подпапке репозитория
export default defineConfig({
  base: './',
  plugins: [
    preact(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['icons/*.png', 'game_data.json'],
      workbox: { globPatterns: ['**/*.{js,css,html,png,webp,json,woff2}'] },
      manifest: {
        name: 'Всем костям на борт!',
        short_name: 'Кости на борт',
        lang: 'ru',
        display: 'standalone',
        background_color: '#efe3c8',
        theme_color: '#3b2a1a',
        icons: [{ src: 'icons/H.png', sizes: '512x512', type: 'image/png' }],
      },
    }),
  ],
  test: { environment: 'node' },
});
