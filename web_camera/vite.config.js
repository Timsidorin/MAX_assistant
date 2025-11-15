import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: {
            '@assets' : path.resolve(__dirname, './assets'),
            '@api' : path.resolve(__dirname, './api'),
            '@helpers' : path.resolve(__dirname, './helpers'),
        }
    },
    define: {
        __BASE__PYTHON__URL__: JSON.stringify('https://zestfully-champion-parakeet.cloudpub.ru')
    },
    server: {
        allowedHosts: ['untimely-eligible-pheasant.cloudpub.ru', 'pulseai.knastu.ru'],
        port: 8006,
        host: '0.0.0.0',
    },
})
