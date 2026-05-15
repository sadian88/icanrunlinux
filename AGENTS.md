# AGENTS.md — I Can Run Linux

## Quick start

```sh
python -m venv .venv
source .venv/bin/activate       # use .venv/bin/activate.fish for Fish shell
pip install -r requirements.txt

# 1. Database setup (PostgreSQL + pgvector must be running locally)
export DATABASE_URL="postgresql://user:pass@localhost:5432/linux_compat"
cp .env.example .env   # edit with your credentials

prisma db push          # create tables from schema
psql $DATABASE_URL -f scripts/setup.sql   # enable pgvector + add vector column + ai_recommendations table

# 2. Scrape + migrate
python scripts/scraper.py
python scripts/migrate_json_to_db.py

# 3. Run API
uvicorn app.main:app --reload

# 4. Run frontend
cd frontend && npm install && npm run dev
```

## Project structure

- `scripts/scraper.py` — DistroWatch scraper. Run from repo root. 1.5s delay between requests. Output: `data/distros_raw.json`.
- `scripts/migrate_json_to_db.py` — loads JSON into PostgreSQL, generates embeddings via external API, writes pgvector column. Uses psycopg2 for raw SQL (Prisma ORM doesn't handle pgvector natively).
- `scripts/setup.sql` — enables pgvector extension, adds vector(1536) column, creates IVFFlat index, creates `ai_recommendations` and `distro_technical_notes` tables, adds technical metadata columns (`package_manager`, `init_system`, `release_model`, `technical_notes`).
- `scripts/enrich_technical.py` — uses DeepSeek via OpenRouter to generate technical metadata (package manager, init system, release model, technical analysis) for each distro. Run once after scraping.
- `prisma/schema.prisma` — `Distro` model matching JSON schema. `AiRecommendation` model for query cache. `DistroTechnicalNote` for per-distro technical analysis. Vector column managed via raw SQL. Use `prisma db push` to sync.
- `data/distros_raw.json` — committed scraped output (backup).
- `frontend/` — React 19 + TypeScript + Vite + Tailwind CSS v4 + Framer Motion + Lucide React SPA.
  - `vite.config.ts` — proxies `/api` → `http://127.0.0.1:8000` in dev mode.
  - `src/types/distro.ts` — TypeScript interfaces matching API schemas.
  - `src/services/api.ts` — `recommend()` calls the backend.
  - `src/components/SearchWizard.tsx` — 3-step wizard: hardware specs → use cases → free text.
  - `src/components/DistroCard.tsx` — single result card with match %, stats, source badge, and AI reasoning.
  - `src/components/ResultsList.tsx` — renders cards in a list.
- `app/` — FastAPI backend (API + matching engine).
  - `app/main.py` — FastAPI app entrypoint, CORS enabled.
  - `app/config.py` — settings from env vars.
  - `app/models/distro.py` — Pydantic schemas (`DistroOut`, `RecommendRequest`, `RecommendResult`, `AiDistroSuggestion`).
  - `app/routers/distros.py` — `GET /distros` with filters (slug, difficulty, use_case, architecture, min_ram, max_ram).
  - `app/routers/recommend.py` — `POST /recommend` with hybrid matching (cache → pgvector → LLM).
  - `app/services/db.py` — psycopg2 connection + dict row factory.
  - `app/services/embedding.py` — calls external embeddings API.
  - `app/services/matching.py` — three-tier matching: AI cache → pgvector → LLM fallback + self-enrichment. Includes technical metadata in embeddings for richer semantic search.
  - `app/services/llm.py` — DeepSeek via OpenRouter chat completions.
  - `app/services/ai_cache.py` — query-level vector cache in `ai_recommendations` table.

## Database

- PostgreSQL with pgvector. Connection via `DATABASE_URL`.
- Embeddings stored in `distros.embedding` as `vector(1536)`. Managed via raw SQL (psycopg2), not Prisma ORM.
- Embedding dimension controlled by `EMBEDDINGS_DIMENSIONS` env var.
- `ai_recommendations` table stores previous LLM responses with `query_embedding` for cache hits.

## Embeddings

- OpenAI-compatible API. Configured via env: `EMBEDDINGS_API_URL`, `EMBEDDINGS_API_KEY`, `EMBEDDINGS_MODEL`, `EMBEDDINGS_DIMENSIONS`.
- `migrate_json_to_db.py` batches 20 distros per API call. Text built from name + description + use_cases + categories + desktop.
- API auto-appends `/embeddings` to the URL if missing.

## LLM / AI Matching

- **Model:** DeepSeek via OpenRouter (`deepseek/deepseek-chat`).
- **Config:** `LLM_API_URL`, `LLM_API_KEY`, `LLM_MODEL` in `.env`.
- **Threshold:** `MATCH_THRESHOLD=0.5` — if best pgvector match is below this, fallback to LLM.
- **Cache:** `AI_CACHE_THRESHOLD=0.92` — cosine similarity needed to reuse a cached LLM response.

### Three-tier matching flow (`POST /recommend`)

1. **AI Cache** — embed query, search `ai_recommendations` by vector similarity. If match >= 0.92, return cached distros instantly.
2. **pgvector Search** — query `distros` table with real cosine similarity (`1 - (embedding <=> vector)`). `use_cases` are a soft boost (+0.15) not a hard filter.
3. **LLM Fallback** — if best DB match < 0.5, call DeepSeek. Parse JSON response, save to `ai_recommendations` cache, insert new distros into `distros` table (self-enrichment), and return results.

### Self-enrichment

When the LLM suggests a distro not in the database:
- A new row is inserted into `distros` with an auto-generated embedding.
- Future queries can match against this AI-enriched distro via pgvector.
- The distro's `source` field in the API response is `"llm"`.

## Scraper behavior

- Extracts top 50 distros by popularity rank from DistroWatch.
- `enrich_distro_basic()` at `scraper.py:162` applies hardcoded heuristics for `use_cases` and `difficulty`. Modify there.
- Regex-based table parsing (lines 111–141) is the most fragile section if DistroWatch HTML changes.

## Commands

```sh
ruff check scripts/ tests/ app/   # lint
pytest -v                          # test
prisma db push                     # sync schema to DB
prisma generate                    # regenerate Prisma client
psql $DATABASE_URL -f scripts/setup.sql   # pgvector + ai_recommendations + technical columns setup
python scripts/scraper.py          # scrape distrowatch
python scripts/migrate_json_to_db.py      # load into DB
python scripts/enrich_technical.py  # enrich DB with technical metadata (AI)
python scripts/scraper_repology.py  # fetch package statistics from Repology
python scripts/scraper_phoronix.py  # fetch benchmark data from Phoronix
uvicorn app.main:app --reload      # dev server (API)
curl http://127.0.0.1:8000/docs    # Swagger UI
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/distros` | List distros. Filters: `slug`, `difficulty`, `use_case`, `architecture`, `min_ram`, `max_ram`, `limit` |
| `POST` | `/recommend` | Match distros to user needs. Body: `ram_gb`, `storage_gb`, `use_cases`, `architecture`, `difficulty`, `free_text`, `limit` |

When `free_text` is provided, the query is embedded and pgvector cosine similarity (`<=>`) is used for ranking. Without `free_text`, results are ordered by `popularity_rank`.

Response includes:
- `similarity`: real cosine similarity (0-1)
- `source`: `"database" | "ai_cache" | "llm"`
- `ai_reason`: explanation when source is `"llm"`

## Testing

- `pytest` with mocked HTML (scraper), mocked DB (API), no database dependency for unit tests.
- Tests in `tests/`: `test_enrich.py` (enrichment heuristics), `test_scraper.py` (scraper parsing), `test_api.py` (FastAPI endpoints).
- CI runs `ruff check` + `pytest` on push/PR to main.

## No linter/formatter pre-commit

Lint is CI-only. No pre-commit hooks. Format manually with `ruff format scripts/ tests/ app/` if needed.
