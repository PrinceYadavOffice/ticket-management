# Database Setup Notes

## Overview

- **Engine:** SQLite
- **ORM:** SQLAlchemy 2.x
- **Migrations:** Alembic (`src/backend/alembic/versions/`)
- **Seed data:** `database/seed-data/`
- **Database file:** `data/tickets.db` (repo root, gitignored)

## Directory Layout

```
database/
├── migrations/              # Reference docs
├── seed-data/
│   ├── users.json           # Fictional user definitions
│   └── sample_data.json     # Sample tickets and comments
└── setup-notes.md

data/
└── tickets.db               # Created after migration (gitignored)
```

## First-Time Setup

```bash
# From repository root
cp .env.example .env

cd src/backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Apply schema
alembic upgrade head

# Load fictional users, tickets, and comments (idempotent)
python -m app.scripts.seed

# Start API
uvicorn app.main:app --reload --port 8000
```

## Environment

Optional `.env` at repository root:

```env
DATABASE_URL=sqlite:///./data/tickets.db
CORS_ORIGINS=http://localhost:5173
```

If unset, the app defaults to an absolute path: `data/tickets.db` under the repository root.

## Seed Script

```bash
cd src/backend
source .venv/bin/activate
python -m app.scripts.seed
```

- **Idempotent:** safe to run multiple times; skips existing users (by email), tickets (by title), and comments (by ticket + message + author).
- **Users:** 4 fictional agents/admins from `users.json`
- **Sample data:** 6 tickets and 6 comments from `sample_data.json`

Expected output:

```
Seed complete: 4 users, 6 tickets, 6 comments
```

## Migration Workflow

```bash
cd src/backend
source .venv/bin/activate

# Apply all migrations
alembic upgrade head

# Create new migration after model changes
alembic revision --autogenerate -m "description"
alembic upgrade head

# Roll back one revision
alembic downgrade -1
```

### Current revisions

| Revision | Description |
|----------|-------------|
| `001_initial` | `users`, `tickets`, `comments` tables with indexes and FKs |

## Verify Setup

```bash
cd src/backend
source .venv/bin/activate
pytest ../../tests -q
```

Or quick smoke test:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/users
curl -H "X-User-Id: 1" http://localhost:8000/api/tickets/export.csv
```

## Testing Database

Pytest uses an in-memory SQLite database (see `tests/conftest.py`). Tests do not modify `data/tickets.db`.

## Notes

- Do not edit applied Alembic migration files; create new revisions instead.
- Timestamps stored in UTC.
- Foreign keys: `assigned_to_user_id` nullable; `created_by_user_id` required on tickets and comments.
