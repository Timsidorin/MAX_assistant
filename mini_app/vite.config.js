import { defineConfig } from 'vite';
import path from 'path';
import react from '@vitejs/plugin-react';

export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            '@assets' : path.resolve(__dirname, './assets'),
        }
    },
    define: {
        __BASE__PYTHON__URL__: JSON.stringify('https://zestfully-champion-parakeet.cloudpub.ru')
    },
    //для разработки внутри мини аппы
    server: {
        allowedHosts: ['creakily-patient-eland.cloudpub.ru']
    },
})
