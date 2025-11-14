-- Удаляем таблицу и enum тип, если существуют
DROP TABLE IF EXISTS tasks CASCADE;
DROP TYPE IF EXISTS taskstatus CASCADE;

-- Создаём enum тип с верхним регистром (совместимый с вашим Python enum)
CREATE TYPE taskstatus AS ENUM ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED');

-- Обеспечиваем наличие расширения для генерации UUID
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Создаём таблицу tasks
CREATE TABLE tasks (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(max_user_id) ON DELETE SET NULL,
    description TEXT NOT NULL,
    status taskstatus NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Создаём индексы
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_uuid ON tasks(uuid);

-- Добавляем 10 начальных заданий
INSERT INTO tasks (user_id, description, status) VALUES
(NULL, 'Осмотреть и зафиксировать новые ямы на центральных улицах', 'PENDING'),
(NULL, 'Проверить состояние ремонтных работ ям на проспекте Мира', 'PENDING'),
(NULL, 'Составить отчет о ямах, образовавшихся после зимы', 'PENDING'),
(NULL, 'Контролировать своевременный ремонт ям в жилом районе', 'PENDING'),
(NULL, 'Провести фотофиксацию крупных ям для отчета', 'PENDING'),
(NULL, 'Оценить опасность ям в зоне школьных маршрутов', 'PENDING'),
(NULL, 'Проверить качество заплат после ремонта ям', 'PENDING'),
(NULL, 'Зафиксировать случаи образования ям по улице Ленина', 'PENDING'),
(NULL, 'Провести мониторинг динамики появления ям в округе', 'PENDING'),
(NULL, 'Составить список приоритетных участков с ямами для ремонта', 'PENDING');
