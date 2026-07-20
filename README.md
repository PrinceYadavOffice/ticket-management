# Support Ticket Management System

AI-assisted full-stack project for managing support tickets with comments, status workflows, and CSV export.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, TypeScript, Vite, Vitest, React Testing Library |
| Backend | FastAPI, SQLAlchemy, Alembic, Pydantic |
| Database | SQLite |
| Testing | Pytest (backend), Vitest + RTL (frontend) |

## Acting-User Context (Not Authentication)

The frontend will use a **seeded current-user selector**. The selected user's ID is sent via the `X-User-Id` header on endpoints that need acting-user context (ticket create, comment create, CSV export). This is **not** authentication.

## API Base URL

```
http://localhost:8000
```

Interactive docs: `http://localhost:8000/docs`

## Quick Start

### Backend

```bash
cd src/backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Optional: cp ../../.env.example ../../.env
alembic upgrade head
python -m app.scripts.seed
uvicorn app.main:app --reload --port 8000
```

### Verify

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/users
curl "http://localhost:8000/api/tickets?page=1&pageSize=10"
curl -H "X-User-Id: 1" http://localhost:8000/api/tickets/export.csv
```

### Run Backend Tests

```bash
cd src/backend && source .venv/bin/activate && pytest ../../tests -v
```

### Frontend (scaffold)

```bash
cd src/frontend
npm install
npm run dev
```

## API Endpoints

| Method | Path | X-User-Id |
|--------|------|-----------|
| GET | `/health` | No |
| GET | `/api/users` | No |
| POST | `/api/tickets` | **Yes** |
| GET | `/api/tickets` | No |
| GET | `/api/tickets/export.csv` | **Yes** |
| GET | `/api/tickets/{ticketId}` | No |
| PATCH | `/api/tickets/{ticketId}` | No |
| PATCH | `/api/tickets/{ticketId}/status` | No |
| POST | `/api/tickets/{ticketId}/comments` | **Yes** |

Full specification: [api-contract.md](./api-contract.md)

## Repository Layout

```
├── src/backend/          # FastAPI app (implemented)
├── src/frontend/         # React app (scaffold)
├── tests/                # Pytest (40 tests)
├── database/seed-data/   # Seed JSON files
├── data/tickets.db       # SQLite file (gitignored, created on migrate)
└── api-contract.md       # API specification
```

## Implementation Status

| Component | Status |
|-----------|--------|
| Backend API | **Complete** (Core) |
| Database + migrations | **Complete** |
| Seed script | **Complete** |
| Backend tests | **40 passing** |
| Frontend UI | Scaffold only (M5) |

## Documentation

| Document | Purpose |
|----------|---------|
| [api-contract.md](./api-contract.md) | REST API specification |
| [data-model.md](./data-model.md) | Database schema |
| [database/setup-notes.md](./database/setup-notes.md) | DB setup instructions |
| [design-notes.md](./design-notes.md) | Architecture |
| [ui-flow.md](./ui-flow.md) | Frontend design (not yet implemented) |

## Core vs Stretch

**Core:** Ticket CRUD, comments, status state machine, search/filter/pagination, CSV export, backend validation.

**Stretch:** Real authentication, role-based UI, deployment automation.

See [acceptance-criteria.md](./acceptance-criteria.md).
