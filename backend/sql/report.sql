-- Удаляем таблицу и enum-типы, если существуют
DROP TABLE IF EXISTS reports CASCADE;
DROP TYPE IF EXISTS reportstatus CASCADE;
DROP TYPE IF EXISTS reportpriority CASCADE;

-- Создаём enum типы для статуса и приоритета
CREATE TYPE reportstatus AS ENUM (
    'draft', 
    'submitted', 
    'in_review', 
    'in_progress', 
    'completed'
);

CREATE TYPE reportpriority AS ENUM (
    'low', 
    'medium', 
    'high', 
    'critical'
);

-- Создаём таблицу reports
CREATE TABLE reports (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(max_user_id) ON DELETE SET NULL,
    latitude TEXT,
    longitude TEXT,
    address TEXT,
    image_url TEXT,
    image_urls JSONB,
    video_url TEXT,
    total_potholes INTEGER NOT NULL DEFAULT 0,
    average_risk DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    max_risk DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    critical_count INTEGER NOT NULL DEFAULT 0,
    high_count INTEGER NOT NULL DEFAULT 0,
    medium_count INTEGER NOT NULL DEFAULT 0,
    low_count INTEGER NOT NULL DEFAULT 0,
    status reportstatus NOT NULL DEFAULT 'draft',
    priority reportpriority NOT NULL DEFAULT 'low',
    description TEXT,
    comment TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    submitted_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    ai_agent_task_id TEXT,
    ai_agent_status TEXT,
    organization_name TEXT,
    external_tracking_id TEXT
);

-- Создаём индексы для удобства запросов
CREATE INDEX idx_reports_user_id ON reports(user_id);
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_priority ON reports(priority);
CREATE INDEX idx_reports_created_at ON reports(created_at);