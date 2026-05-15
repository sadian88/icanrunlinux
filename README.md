# I Can Run Linux

Find the best Linux distribution for your hardware using AI-powered matching and pgvector similarity search.

## Quick start

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> **Fish shell users:** Use `source .venv/bin/activate.fish` instead of `source .venv/bin/activate`.

### 1. Database setup (PostgreSQL + pgvector)

```sh
export DATABASE_URL="postgresql://user:pass@localhost:5432/linux_compat"
cp .env.example .env   # edit with your credentials

prisma db push          # create tables from schema
psql $DATABASE_URL -f scripts/setup.sql   # enable pgvector + add vector column
```

### 2. Scrape + migrate

```sh
python scripts/scraper.py
python scripts/migrate_json_to_db.py
```

### 3. Run API

```sh
uvicorn app.main:app --reload
```

### 4. Run frontend

```sh
cd frontend && npm install && npm run dev
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/distros` | List distros with filters |
| `POST` | `/recommend` | Match distros to user needs |

## Tech stack

- **Backend:** FastAPI, PostgreSQL, pgvector, Prisma, psycopg2
- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS v4, Framer Motion, Lucide React
- **Embeddings:** OpenAI-compatible API (configurable via env vars)

## Commands

```sh
ruff check scripts/ tests/ app/   # lint
pytest -v                          # test
prisma db push                     # sync schema to DB
prisma generate                    # regenerate Prisma client
```
