CREATE TABLE users (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    max_user_id INTEGER UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    registration_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX idx_max_user_id ON users(max_user_id);
CREATE INDEX idx_first_name ON users(first_name);
CREATE INDEX idx_last_name ON users(last_name);
CREATE INDEX idx_username ON users(username);