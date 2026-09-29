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
        __BASE__PYTHON__URL__: JSON.stringify('https://excellently-sterling-roundworm.cloudpub.ru')
    },
    server: {
        allowedHosts: ['permissibly-still-badger.cloudpub.ru', 'avowedly-oriented-dodo.cloudpub.ru'],
        port: 8006,
        host: '0.0.0.0',
    },
})
