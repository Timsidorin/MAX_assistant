import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: {
            '@assets' : path.resolve(__dirname, './assets'),
        }
    },
    //для разработки внутри мини аппы
    server: {
        allowedHosts: ['creakily-patient-eland.cloudpub.ru']
    }
})
