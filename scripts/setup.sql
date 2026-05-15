-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Add vector column to distros table (run after prisma db push)
ALTER TABLE distros ADD COLUMN IF NOT EXISTS embedding vector(1536);

-- Add technical metadata columns
ALTER TABLE distros ADD COLUMN IF NOT EXISTS package_manager TEXT DEFAULT '';
ALTER TABLE distros ADD COLUMN IF NOT EXISTS init_system TEXT DEFAULT '';
ALTER TABLE distros ADD COLUMN IF NOT EXISTS release_model TEXT DEFAULT '';
ALTER TABLE distros ADD COLUMN IF NOT EXISTS technical_notes TEXT DEFAULT '';

-- Create index for approximate nearest neighbor search
CREATE INDEX IF NOT EXISTS idx_distros_embedding ON distros USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- AI recommendations cache table
CREATE TABLE IF NOT EXISTS ai_recommendations (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    query_embedding vector(1536),
    response_json JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ai_recommendations_embedding ON ai_recommendations USING ivfflat (query_embedding vector_cosine_ops) WITH (lists = 50);
CREATE INDEX IF NOT EXISTS idx_ai_recommendations_created_at ON ai_recommendations(created_at);

-- Technical notes for per-distro technical analysis
CREATE TABLE IF NOT EXISTS distro_technical_notes (
    id SERIAL PRIMARY KEY,
    distro_id INTEGER NOT NULL REFERENCES distros(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding vector(1536),
    source TEXT DEFAULT 'ai',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_technical_notes_embedding ON distro_technical_notes USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);
CREATE INDEX IF NOT EXISTS idx_technical_notes_distro_id ON distro_technical_notes(distro_id);

-- Phoronix benchmark results per distro
CREATE TABLE IF NOT EXISTS distro_benchmarks (
    id SERIAL PRIMARY KEY,
    distro_id INTEGER NOT NULL REFERENCES distros(id) ON DELETE CASCADE,
    test_name TEXT NOT NULL,
    score DOUBLE PRECISION NOT NULL,
    unit TEXT DEFAULT '',
    source_url TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_benchmarks_distro_id ON distro_benchmarks(distro_id);

-- Repology package statistics per distro
CREATE TABLE IF NOT EXISTS distro_package_stats (
    id SERIAL PRIMARY KEY,
    distro_id INTEGER NOT NULL REFERENCES distros(id) ON DELETE CASCADE,
    total_packages INTEGER DEFAULT 0,
    outdated_packages INTEGER DEFAULT 0,
    vulnerable_packages INTEGER DEFAULT 0,
    newest_packages INTEGER DEFAULT 0,
    problematic_packages INTEGER DEFAULT 0,
    source_url TEXT DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_package_stats_distro_id ON distro_package_stats(distro_id);
