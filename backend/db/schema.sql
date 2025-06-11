-- RecallGuard relational schema (PostgreSQL)
-- =========================================
-- NOTE: run with psql -f schema.sql (or Alembic migrations will generate
-- equivalent DDL automatically from SQLAlchemy models, but this file is
-- helpful for manual boot‑strapping / reference).

-- ----------------------------------------------------------------------
-- ENUM TYPES
-- ----------------------------------------------------------------------

DO $$ BEGIN
    CREATE TYPE recall_source       AS ENUM ('CPSC', 'FDA', 'NHTSA', 'USDA', 'MISC');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE alert_medium        AS ENUM ('email', 'sms', 'push');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE user_tier           AS ENUM ('free', 'pro', 'enterprise');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ----------------------------------------------------------------------
-- CORE TABLES
-- ----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(320) NOT NULL UNIQUE,
    password_hash   VARCHAR(128) NOT NULL,
    full_name       VARCHAR(128),
    tier            user_tier     NOT NULL DEFAULT 'free',
    preferences     JSONB         NOT NULL DEFAULT '{}'::jsonb,
    is_active       BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email_ci ON users (LOWER(email));

-- ----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS products (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER       NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name            TEXT,
    upc             VARCHAR(32),
    vin             VARCHAR(20),
    manual_entry    TEXT,
    vision_hash     TEXT,
    photo_url       TEXT,
    notes           TEXT,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_product_identifier CHECK (upc IS NOT NULL OR vin IS NOT NULL OR manual_entry IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_products_user ON products (user_id);
CREATE INDEX IF NOT EXISTS idx_products_upc  ON products (upc);
CREATE INDEX IF NOT EXISTS idx_products_vin  ON products (vin);

-- ----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS recalls (
    id              SERIAL PRIMARY KEY,
    ext_id          VARCHAR(64) UNIQUE NOT NULL,
    source          recall_source  NOT NULL,
    title           TEXT           NOT NULL,
    description     TEXT,
    hazard          TEXT,
    remedy          TEXT,
    affected_units  TEXT,
    url             TEXT,
    published_at    TIMESTAMPTZ,
    raw_payload     JSONB          NOT NULL,
    created_at      TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_recalls_source_date ON recalls (source, published_at DESC);

-- ----------------------------------------------------------------------

-- Associative table: many‑to‑many between products and recalls
CREATE TABLE IF NOT EXISTS product_recalls (
    product_id      INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    recall_id       INTEGER NOT NULL REFERENCES recalls(id)  ON DELETE CASCADE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (product_id, recall_id)
);

-- ----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS alerts (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER       NOT NULL REFERENCES users(id)   ON DELETE CASCADE,
    recall_id       INTEGER       NOT NULL REFERENCES recalls(id) ON DELETE CASCADE,
    medium          alert_medium  NOT NULL,
    subject         TEXT          NOT NULL,
    body            TEXT          NOT NULL,
    sent_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alerts_user_sent ON alerts (user_id, sent_at DESC);

-- ----------------------------------------------------------------------
-- TRIGGERS
-- ----------------------------------------------------------------------
-- Keep updated_at in sync automatically.
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$ BEGIN
    CREATE TRIGGER trg_users_updated
        BEFORE UPDATE ON users
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TRIGGER trg_products_updated
        BEFORE UPDATE ON products
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ----------------------------------------------------------------------
-- EXTENSIONS (optional but recommended)
-- ----------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- For future UUID / digest helpers

-- ----------------------------------------------------------------------
-- DONE
-- ----------------------------------------------------------------------
