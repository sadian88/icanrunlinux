#!/bin/bash
set -e

echo "=== I Can Run Linux — Backend Entrypoint ==="

# Wait for PostgreSQL to be ready
echo "[entrypoint] Waiting for database..."
for i in $(seq 1 30); do
    if pg_isready -h "${DB_HOST:-db}" -p "${DB_PORT:-5432}" -U "${DB_USER:-postgres}" -d "${DB_NAME:-linux_compat}" -t 3 2>/dev/null; then
        echo "[entrypoint] Database is ready."
        break
    fi
    echo "[entrypoint] DB not ready, retrying ($i/30)..."
    sleep 2
done

# Check if distros table exists
echo "[entrypoint] Checking if distros table exists..."
TABLE_EXISTS=$(psql "$DATABASE_URL" -t -c "SELECT to_regclass('distros')" 2>/dev/null | tr -d '[:space:]')
echo "[entrypoint] TABLE_EXISTS = '$TABLE_EXISTS'"

if [ "$TABLE_EXISTS" != "distros" ]; then
    echo "[entrypoint] First run: creating tables via prisma db push..."
    prisma db push --skip-generate || {
        echo "[entrypoint] ERROR: prisma db push failed"
        exit 1
    }
    echo "[entrypoint] Running setup.sql (pgvector extension, vector columns, indexes)..."
    psql "$DATABASE_URL" -f scripts/setup.sql || {
        echo "[entrypoint] ERROR: setup.sql failed"
        exit 1
    }
else
    echo "[entrypoint] Tables exist. Running setup.sql for idempotent updates..."
    psql "$DATABASE_URL" -f scripts/setup.sql 2>&1 || true
fi

# Check distro count and run scraper if needed
echo "[entrypoint] Checking distro count..."
DISTRO_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM distros" 2>/dev/null | tr -d '[:space:]')
echo "[entrypoint] DISTRO_COUNT = '$DISTRO_COUNT'"

if [ "$DISTRO_COUNT" = "0" ] || [ -z "$DISTRO_COUNT" ]; then
    echo "[entrypoint] No distros found. Running scraper + migration..."
    mkdir -p data
    echo "[entrypoint] Running scraper.py..."
    python scripts/scraper.py || {
        echo "[entrypoint] ERROR: scraper failed"
        exit 1
    }
    echo "[entrypoint] Running migrate_json_to_db.py..."
    python scripts/migrate_json_to_db.py || {
        echo "[entrypoint] ERROR: migration failed"
        exit 1
    }
    echo "[entrypoint] Running scraper_repology.py (package statistics)..."
    python scripts/scraper_repology.py || {
        echo "[entrypoint] WARNING: scraper_repology failed, continuing..."
    }
    echo "[entrypoint] Running scraper_phoronix.py (benchmarks)..."
    python scripts/scraper_phoronix.py || {
        echo "[entrypoint] WARNING: scraper_phoronix failed, continuing..."
    }
else
    echo "[entrypoint] $DISTRO_COUNT distros already in DB. Skipping scraping."
fi

# Check if Repology/Package stats are missing → run supplementary scrapers
PKG_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM distro_package_stats" 2>/dev/null | tr -d '[:space:]')
if [ "$PKG_COUNT" = "0" ] || [ -z "$PKG_COUNT" ]; then
    echo "[entrypoint] No package stats found. Running scraper_repology.py..."
    mkdir -p data
    python scripts/scraper_repology.py || {
        echo "[entrypoint] WARNING: scraper_repology failed, continuing..."
    }
fi

# Check if Benchmarks are missing → run Phoronix scraper
BM_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM distro_benchmarks" 2>/dev/null | tr -d '[:space:]')
if [ "$BM_COUNT" = "0" ] || [ -z "$BM_COUNT" ]; then
    echo "[entrypoint] No benchmarks found. Running scraper_phoronix.py..."
    python scripts/scraper_phoronix.py || {
        echo "[entrypoint] WARNING: scraper_phoronix failed, continuing..."
    }
fi

echo "[entrypoint] Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --forwarded-allow-ips '*'
