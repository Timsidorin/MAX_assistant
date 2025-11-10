
CREATE TABLE reports (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER,
    latitude VARCHAR(50),
    longitude VARCHAR(50),
    address VARCHAR(500),
    image_url VARCHAR(1000),
    image_urls JSONB,
    video_url VARCHAR(1000),
    total_potholes INTEGER DEFAULT 0 NOT NULL,
    average_risk FLOAT DEFAULT 0.0 NOT NULL,
    max_risk FLOAT DEFAULT 0.0 NOT NULL,
    critical_count INTEGER DEFAULT 0 NOT NULL,
    high_count INTEGER DEFAULT 0 NOT NULL,
    medium_count INTEGER DEFAULT 0 NOT NULL,
    low_count INTEGER DEFAULT 0 NOT NULL,
    status reportstatus DEFAULT 'draft' NOT NULL,
    priority reportpriority DEFAULT 'medium' NOT NULL,
    description TEXT,
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    CONSTRAINT fk_reports_user_id
        FOREIGN KEY (user_id)
        REFERENCES users(max_user_id)
        ON DELETE SET NULL
);

CREATE INDEX ix_reports_uuid ON reports(uuid);
CREATE INDEX ix_reports_user_id ON reports(user_id);
CREATE INDEX ix_reports_status ON reports(status);
