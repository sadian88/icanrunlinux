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

-- AI recommendations cache table (table created by Prisma, add pgvector column)
ALTER TABLE ai_recommendations ADD COLUMN IF NOT EXISTS query_embedding vector(1536);

CREATE INDEX IF NOT EXISTS idx_ai_recommendations_embedding ON ai_recommendations USING ivfflat (query_embedding vector_cosine_ops) WITH (lists = 50);
CREATE INDEX IF NOT EXISTS idx_ai_recommendations_created_at ON ai_recommendations(created_at);

-- Technical notes for per-distro technical analysis (table created by Prisma, add pgvector column)
ALTER TABLE distro_technical_notes ADD COLUMN IF NOT EXISTS embedding vector(1536);

CREATE INDEX IF NOT EXISTS idx_technical_notes_embedding ON distro_technical_notes USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);
CREATE INDEX IF NOT EXISTS idx_technical_notes_distro_id ON distro_technical_notes(distro_id);

-- Phoronix benchmark results per distro (table created by Prisma)
CREATE INDEX IF NOT EXISTS idx_benchmarks_distro_id ON distro_benchmarks(distro_id);

-- Repology package statistics per distro (table created by Prisma)
CREATE INDEX IF NOT EXISTS idx_package_stats_distro_id ON distro_package_stats(distro_id);
