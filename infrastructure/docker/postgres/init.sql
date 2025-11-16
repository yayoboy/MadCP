-- ============================================================================
-- MadCP - PostgreSQL Initialization Script
-- ============================================================================
--
-- This script initializes the PostgreSQL database for MadCP
-- It runs automatically when the container is first created
--
-- ============================================================================

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- For better indexing

-- Create schemas
CREATE SCHEMA IF NOT EXISTS madcp;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Set search path
SET search_path TO madcp, public;

-- ============================================================================
-- Tables
-- ============================================================================

-- Repositories table
CREATE TABLE IF NOT EXISTS madcp.repositories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    branch VARCHAR(255) DEFAULT 'main',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_analyzed_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    UNIQUE(url, branch)
);

-- Analysis results table
CREATE TABLE IF NOT EXISTS madcp.analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repository_id UUID REFERENCES madcp.repositories(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    languages_detected TEXT[],
    total_files INTEGER DEFAULT 0,
    total_lines INTEGER DEFAULT 0,
    metrics JSONB,
    dependencies JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);

-- Code files table
CREATE TABLE IF NOT EXISTS madcp.code_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repository_id UUID REFERENCES madcp.repositories(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    language VARCHAR(50),
    content TEXT,
    content_hash VARCHAR(64),
    lines_of_code INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(repository_id, file_path)
);

-- Embeddings table
CREATE TABLE IF NOT EXISTS madcp.embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id UUID REFERENCES madcp.code_files(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    vector_id VARCHAR(255),  -- ID in vector database
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(file_id, chunk_index)
);

-- Issues table (for planning)
CREATE TABLE IF NOT EXISTS madcp.issues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repository_id UUID REFERENCES madcp.repositories(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    priority VARCHAR(50),
    category VARCHAR(100),
    estimated_effort VARCHAR(50),
    status VARCHAR(50) DEFAULT 'open',
    affected_files TEXT[],
    labels TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- ============================================================================
-- Indexes
-- ============================================================================

-- Repositories indexes
CREATE INDEX IF NOT EXISTS idx_repositories_status ON madcp.repositories(status);
CREATE INDEX IF NOT EXISTS idx_repositories_created_at ON madcp.repositories(created_at DESC);

-- Analysis results indexes
CREATE INDEX IF NOT EXISTS idx_analysis_repository ON madcp.analysis_results(repository_id);
CREATE INDEX IF NOT EXISTS idx_analysis_status ON madcp.analysis_results(status);
CREATE INDEX IF NOT EXISTS idx_analysis_created_at ON madcp.analysis_results(created_at DESC);

-- Code files indexes
CREATE INDEX IF NOT EXISTS idx_files_repository ON madcp.code_files(repository_id);
CREATE INDEX IF NOT EXISTS idx_files_language ON madcp.code_files(language);
CREATE INDEX IF NOT EXISTS idx_files_path_trgm ON madcp.code_files USING gin(file_path gin_trgm_ops);

-- Embeddings indexes
CREATE INDEX IF NOT EXISTS idx_embeddings_file ON madcp.embeddings(file_id);

-- Issues indexes
CREATE INDEX IF NOT EXISTS idx_issues_repository ON madcp.issues(repository_id);
CREATE INDEX IF NOT EXISTS idx_issues_status ON madcp.issues(status);
CREATE INDEX IF NOT EXISTS idx_issues_priority ON madcp.issues(priority);

-- ============================================================================
-- Functions
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION madcp.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ============================================================================
-- Triggers
-- ============================================================================

-- Trigger for repositories
DROP TRIGGER IF EXISTS update_repositories_updated_at ON madcp.repositories;
CREATE TRIGGER update_repositories_updated_at
    BEFORE UPDATE ON madcp.repositories
    FOR EACH ROW
    EXECUTE FUNCTION madcp.update_updated_at_column();

-- Trigger for code_files
DROP TRIGGER IF NOT EXISTS update_code_files_updated_at ON madcp.code_files;
CREATE TRIGGER update_code_files_updated_at
    BEFORE UPDATE ON madcp.code_files
    FOR EACH ROW
    EXECUTE FUNCTION madcp.update_updated_at_column();

-- Trigger for issues
DROP TRIGGER IF EXISTS update_issues_updated_at ON madcp.issues;
CREATE TRIGGER update_issues_updated_at
    BEFORE UPDATE ON madcp.issues
    FOR EACH ROW
    EXECUTE FUNCTION madcp.update_updated_at_column();

-- ============================================================================
-- Analytics Schema
-- ============================================================================

-- Usage statistics table
CREATE TABLE IF NOT EXISTS analytics.usage_stats (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(255),
    method VARCHAR(10),
    status_code INTEGER,
    response_time_ms FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create hypertable for time-series data (if TimescaleDB is available)
-- SELECT create_hypertable('analytics.usage_stats', 'timestamp', if_not_exists => TRUE);

-- ============================================================================
-- Permissions
-- ============================================================================

-- Grant permissions to madcp user
GRANT ALL PRIVILEGES ON SCHEMA madcp TO madcp;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA madcp TO madcp;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA madcp TO madcp;

GRANT ALL PRIVILEGES ON SCHEMA analytics TO madcp;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA analytics TO madcp;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA analytics TO madcp;

-- ============================================================================
-- Sample Data (Development Only)
-- ============================================================================

-- Insert sample repository
-- INSERT INTO madcp.repositories (name, url, branch, description)
-- VALUES ('sample-repo', 'https://github.com/example/repo', 'main', 'Sample repository for testing')
-- ON CONFLICT (url, branch) DO NOTHING;

-- ============================================================================
-- End of Initialization Script
-- ============================================================================
