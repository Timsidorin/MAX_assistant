-- Создаём таблицу users
CREATE TABLE users (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    max_user_id INTEGER UNIQUE,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    username VARCHAR(50) UNIQUE,
    registration_at TIMESTAMP,
    sent_reports_count INTEGER NOT NULL DEFAULT 0,
    user_level INTEGER NOT NULL DEFAULT 1,
    current_status VARCHAR(100),
    total_points INTEGER NOT NULL DEFAULT 0
);

-- Индексы для ускорения поиска
CREATE INDEX idx_users_max_user_id ON users(max_user_id);
CREATE INDEX idx_users_first_name ON users(first_name);
CREATE INDEX idx_users_last_name ON users(last_name);
CREATE INDEX idx_users_username ON users(username);