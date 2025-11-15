import { defineConfig } from 'vite';
import path from 'path';
import react from '@vitejs/plugin-react';

export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            '@components' : path.resolve(__dirname, './components'),
            '@assets' : path.resolve(__dirname, './assets'),
            '@api' : path.resolve(__dirname, './api'),
            '@hooks' : path.resolve(__dirname, './hooks'),
            '@pages' : path.resolve(__dirname, './pages'),
        }
    },
    define: {
        __BASE__PYTHON__URL__: JSON.stringify('https://zestfully-champion-parakeet.cloudpub.ru'),
        __BASE__SCANNER__URL__: JSON.stringify('https://untimely-eligible-pheasant.cloudpub.ru'),
    },
    //для разработки внутри мини аппы
    server: {
        allowedHosts: ['creakily-patient-eland.cloudpub.ru'],
        port: 8008,
    },
})
