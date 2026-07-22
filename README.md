# Support Ticket Management System

A full-stack support ticket application with comments, backend-enforced status workflows, search/filter, and CSV export. Built with FastAPI and React; data persists in SQLite across restarts.

**Acting-user context:** The UI selects a seeded user and sends `X-User-Id` on certain API calls. This simulates who is acting — it is **not** authentication.

---

## Features (Core — implemented)

| Area | Capabilities |
|------|----------------|
| **Tickets** | Create, list, detail, update title/description/priority/assignee |
| **Status workflow** | Backend state machine: Open → In Progress/Cancelled → Resolved/Cancelled → Closed |
| **Comments** | Add comments on ticket detail; author and timestamp recorded |
| **Search & filter** | Keyword search, filter by status, priority, assignee, unassigned; pagination |
| **CSV export** | Download tickets **created by** the acting user |
| **Acting user** | Seeded user selector with `localStorage` persistence |
| **Validation** | Backend Pydantic validation + frontend required-field checks and API error display |

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, TypeScript, Vite 5, React Router 6 |
| Frontend tests | Vitest, React Testing Library, jsdom |
| Backend | FastAPI, Pydantic v2, SQLAlchemy 2 |
| Migrations | Alembic |
| Database | SQLite (`data/tickets.db`, gitignored) |
| Backend tests | Pytest, FastAPI TestClient |

---

## Prerequisites

- **Python** 3.10+ (verified with 3.10.14)
- **Node.js** 18+ and npm
- **Git**

---

## Environment Setup

Optional root `.env` (copy from `.env.example`):

```bash
cp .env.example .env
```

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | `sqlite:///.../data/tickets.db` | SQLite path |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed frontend origin |
| `VITE_API_BASE_URL` | `http://localhost:8000` | Frontend API base (set in frontend `.env` if needed) |

---

## Backend Setup

```bash
cd src/backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Migration command

From `src/backend` with venv active:

```bash
alembic upgrade head
```

Creates `data/tickets.db` at repository root (via config path resolution).

### Seed command

```bash
python -m app.scripts.seed
```

Idempotent — safe to run multiple times. Seeds 4 users and sample tickets/comments from `database/seed-data/`.

### Run backend

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Health: http://localhost:8000/health  
- OpenAPI docs: http://localhost:8000/docs  

---

## Frontend Setup

```bash
cd src/frontend
npm install          # or npm ci for clean install
npm run dev
```

Open http://localhost:5173 — **backend must be running on port 8000**.

---

## Test Commands

**Backend** (from repository root, venv active):

```bash
cd src/backend && source .venv/bin/activate
pytest ../../tests -v
```

68 tests; isolated SQLite per test (`tmp_path/pytest_tickets.db`) — never uses production `data/tickets.db`.

**Frontend:**

```bash
cd src/frontend
npm test
```

25 tests (Vitest).

---

## Build Command

```bash
cd src/frontend
npm run build
```

Runs `tsc --noEmit` then `vite build` → output in `src/frontend/dist/` (gitignored).

---

## State Machine Rules

Enforced in `src/backend/app/services/status_machine.py`. Invalid transitions return **HTTP 409** `INVALID_STATUS_TRANSITION`.

| Current status | Allowed transitions |
|----------------|---------------------|
| **Open** | In Progress, Cancelled |
| **In Progress** | Resolved, Cancelled |
| **Resolved** | Closed |
| **Closed** | *(none — terminal)* |
| **Cancelled** | *(none — terminal)* |

Status is changed only via `PATCH /api/tickets/{id}/status`, not the general ticket update endpoint. The UI renders buttons from `allowedStatusTransitions` returned by the API.

---

## Search and Filter Behavior

**API query parameters** (`GET /api/tickets`):

| Parameter | Description |
|-----------|-------------|
| `q` | Case-insensitive search in title and description |
| `status` | Exact status match |
| `priority` | Exact priority match |
| `assignedTo` | Assignee user ID |
| `unassigned` | `true` — only unassigned tickets |
| `page` | Page number (default 1) |
| `pageSize` | Page size (default 20, max 100) |

Filters combine with **AND** logic. Frontend applies filters on **Apply filters** click (`TicketFilters` → `TicketListPage`).

---

## Current-User Selector

| Aspect | Detail |
|--------|--------|
| Component | `ActingUserSelector` in app header |
| Data source | `GET /api/users` |
| Persistence | `localStorage` key `actingUserId` |
| Header sent | `X-User-Id: <id>` on ticket create, comment create, CSV export |
| Disclaimer | Visible in `AppLayout` — not authentication |

---

## CSV Export

1. Select acting user in header.
2. On ticket list page, click **Export My Tickets (CSV)**.
3. Browser downloads CSV for tickets where `createdBy` equals the acting user (not assigned tickets).

API: `GET /api/tickets/export.csv` with `X-User-Id` header. Formula-injection prefixes sanitized in `csv_export.py`.

---

## API Endpoints

| Method | Path | X-User-Id required |
|--------|------|-------------------|
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

---

## Project Structure

```
├── README.md                    # This file
├── acceptance-criteria.md       # Core acceptance checklist
├── compliance-checklist.md      # Requirement → file mapping
├── api-contract.md              # REST API spec
├── data-model.md                # Database schema
├── design-notes.md              # Architecture
├── ui-flow.md                   # Frontend flows
├── test-strategy.md             # Testing approach
├── test-results.md              # Latest verified test runs
├── requirements-analysis.md     # Functional requirements
├── implementation-plan.md       # Milestones
├── candidate-info.md            # Submission form (fill before submit)
├── tool-workflow.md             # AI-assisted workflow
├── reflection.md                # Post-project reflection
├── pr-description.md            # PR template (filled)
├── final-ai-usage-summary.md    # AI session log
├── ai-prompts/                  # Phase prompt templates + session logs
├── artifacts/prompt-history/    # Detailed prompt history
├── database/seed-data/          # users.json, sample_data.json
├── data/                        # SQLite DB (gitignored)
├── src/backend/                 # FastAPI application
│   ├── app/api/                 # Route handlers
│   ├── app/services/            # Business logic + state machine
│   ├── app/models/              # SQLAlchemy models
│   ├── app/schemas/             # Pydantic schemas
│   ├── alembic/versions/        # Migrations
│   └── app/scripts/seed.py      # Seed script
├── src/frontend/src/            # React application
│   ├── api/                     # API client
│   ├── components/              # UI components
│   ├── context/                 # ActingUserContext
│   └── pages/                   # Route pages
└── tests/                       # Pytest (backend + integration)
```

---

## Troubleshooting

| Problem | Likely cause | Fix |
|---------|--------------|-----|
| Blank page at localhost:5173 | Frontend not running | `cd src/frontend && npm run dev` |
| "Unable to reach server" in UI | Backend not running | Start uvicorn on port 8000 |
| Empty user selector | Backend down or seed not run | Start backend; run `python -m app.scripts.seed` |
| CORS errors | Wrong origin | Ensure frontend on `localhost:5173`; check `CORS_ORIGINS` |
| `ModuleNotFoundError: app` | Wrong directory for pytest | Run from `src/backend` with venv, or `pytest tests` from root |
| Migration errors on fresh clone | No `data/` dir | `alembic upgrade head` creates DB via config |

**Both servers required:** UI at :5173, API at :8000.

---

## Known Limitations (Core)

- No real authentication or role-based permissions
- `X-User-Id` is client-controlled (demo only)
- SQLite single-file DB (not production-scale)
- No CI/CD pipeline in repo
- No Docker Compose one-command start
- List fetch has no request-abort guard (rare stale-data race)
- `TicketCreatePage` has no dedicated page-level RTL test (create flow covered by `TicketForm.test.tsx`)

---

## Stretch Features Not Implemented

| ID | Feature |
|----|---------|
| ST-02 | Role-based permissions (Agent vs Admin enforcement) |
| ST-03 | Assignment notifications |
| ST-04 | Optimistic locking / version field |
| ST-05 | Dark mode |
| ST-06 | Docker Compose dev environment |
| ST-07 | GitHub Actions CI |
| ST-08 | Custom Swagger branding |
| ST-09 | Audit log / ticket history |
| ST-10 | Reopen closed tickets |

**Note:** Pagination (formerly listed as ST-01) **is implemented** in Core API and UI.

---

## Implementation Status

| Component | Status | Verified |
|-----------|--------|----------|
| Backend API | Complete | 68 pytest tests |
| Database + migrations | Complete | `alembic upgrade head` |
| Seed script | Complete | Idempotent double-seed |
| Frontend UI | Complete | Manual + 25 Vitest tests |
| Production build | Pass | `npm run build` |
| Core quality review | Complete | See `code-review-notes.md` |

---

## Documentation Index

| Document | Purpose |
|----------|---------|
| [compliance-checklist.md](./compliance-checklist.md) | Mandatory requirement mapping |
| [acceptance-criteria.md](./acceptance-criteria.md) | Core sign-off criteria |
| [test-results.md](./test-results.md) | Latest test run output |
| [code-review-notes.md](./code-review-notes.md) | Senior review findings |
| [reflection.md](./reflection.md) | Candidate reflection |
| [final-ai-usage-summary.md](./final-ai-usage-summary.md) | AI usage log |

---

## License / Submission

See [candidate-info.md](./candidate-info.md) — replace placeholders before submission.
