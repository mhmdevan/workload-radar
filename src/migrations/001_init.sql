-- Initial schema for workload-radar

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    owner INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    project INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(32) NOT NULL,
    priority INTEGER NOT NULL,
    assignee INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    done_at TIMESTAMP WITHOUT TIME ZONE
);

CREATE TABLE IF NOT EXISTS task_events (
    id SERIAL PRIMARY KEY,
    task INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    type VARCHAR(64) NOT NULL,
    payload JSONB,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    project INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    type VARCHAR(64) NOT NULL,
    params JSONB,
    status VARCHAR(32) NOT NULL,
    result JSONB,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    finished_at TIMESTAMP WITHOUT TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_tasks_project_status_doneat
    ON tasks (project, status, done_at);

CREATE INDEX IF NOT EXISTS idx_task_events_task_created_at
    ON task_events (task, created_at);

CREATE INDEX IF NOT EXISTS idx_reports_project_created_at
    ON reports (project, created_at);
