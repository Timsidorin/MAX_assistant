FROM node:22.15-alpine

WORKDIR /app

# Копируем файлы зависимостей
COPY package*.json ./

# Устанавливаем зависимости
RUN npm ci

# Копируем исходный код
COPY . .

# Собираем приложение для production
RUN npm run build

# Устанавливаем статический сервер
RUN npm install -g serve

# Создаем не-root пользователя для безопасности
RUN addgroup -g 1001 -S nodejs
RUN adduser -S reactjs -u 1001

# Меняем владельца файлов
RUN chown -R reactjs:nodejs /app

USER reactjs

# Открываем порт
EXPOSE 3000

# Запускаем собранное приложение
CMD ["serve", "-s", "dist", "-l", "3000"]