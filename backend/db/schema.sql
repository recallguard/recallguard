CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    user_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE recalls (
    id TEXT NOT NULL,
    product TEXT NOT NULL,
    hazard TEXT,
    recall_date TEXT,
    source TEXT NOT NULL,
    fetched_at TEXT NOT NULL,
    summary_text TEXT,
    next_steps TEXT,
    remedy_updates JSON DEFAULT '[]',
    PRIMARY KEY (id, source)
);

CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    org_name TEXT NOT NULL,
    key TEXT UNIQUE NOT NULL,
    plan TEXT DEFAULT 'free',
    monthly_quota INTEGER DEFAULT 5000,
    requests_this_month INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE channel_subs (
    id SERIAL PRIMARY KEY,
    platform TEXT,
    channel_id TEXT NOT NULL,
    query TEXT NOT NULL,
    source TEXT DEFAULT 'CPSC',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE webhooks (
    id SERIAL PRIMARY KEY,
    api_key_id INTEGER REFERENCES api_keys(id),
    url TEXT NOT NULL,
    query TEXT,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
