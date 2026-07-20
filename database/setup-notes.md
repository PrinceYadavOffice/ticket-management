# Database Setup Notes

## Overview

- **Engine:** SQLite
- **ORM:** SQLAlchemy 2.x
- **Migrations:** Alembic (located in `src/backend/alembic/`)
- **Seed data:** `database/seed-data/`

## Directory Layout

```
database/
├── migrations/          # Reference docs; canonical migrations in src/backend/alembic/
├── seed-data/
│   └── users.json       # Seed user definitions
└── setup-notes.md       # This file
```

## First-Time Setup

```bash
# From repository root
cp .env.example .env

cd src/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create data directory
mkdir -p ../../data

# Run migrations (once implemented)
alembic upgrade head

# Seed users (once implemented)
# python -m app.scripts.seed
```

## Environment

Set in `.env`:

```
DATABASE_URL=sqlite:///../../data/tickets.db
```

Path is relative to `src/backend/` when running Alembic/Uvicorn.

## Migration Workflow

```bash
cd src/backend
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1   # rollback one revision
```

## Notes

- SQLite file stored at `data/tickets.db` (gitignored)
- Use in-memory SQLite for tests: `sqlite:///:memory:`
- Do not edit applied migration files; create new revisions

## Implementation Status

Migrations and seed script planned for M1. See [implementation-plan.md](../../implementation-plan.md).
