# Implementation Phase Prompts

## Purpose

Guide milestone-based feature implementation.

## Template

```
Context: Support Ticket Management System — Milestone [MX]

Read first:
- implementation-plan.md (milestone section)
- api-contract.md
- data-model.md
- .cursor/rules/

Task: [IMPLEMENTATION TASK]

Constraints:
- Match existing code patterns in src/backend and src/frontend
- Backend validation required; meaningful frontend errors
- No authentication in Core
- Run tests after changes

Output: Code + update relevant docs if contract changed.
```

---

## Session: 2026-07-20 — Core Backend (M1–M4)

### User Request (Summary)

Implement complete Core backend: FastAPI, SQLAlchemy, SQLite, Alembic, Pydantic with all API endpoints under `/api/`, state machine, CSV export, seed data, tests.

### Implemented

| Area | Files |
|------|-------|
| Config | `app/core/config.py`, `enums.py`, `exceptions.py`, `dependencies.py` |
| Models | `app/models/user.py`, `ticket.py`, `comment.py` |
| Schemas | `app/schemas/user.py`, `ticket.py`, `comment.py` |
| Services | `status_machine.py`, `ticket_service.py`, `comment_service.py`, `csv_export.py`, `user_service.py` |
| API | `app/api/users.py`, `tickets.py`, `router.py` |
| Migration | `alembic/versions/001_initial.py` |
| Seed | `app/scripts/seed.py`, `database/seed-data/sample_data.json` |
| Tests | 40 tests in `tests/backend/` and `tests/integration/` |

### API Endpoints (live)

| Method | Path |
|--------|------|
| GET | `/health` |
| GET | `/api/users` |
| POST | `/api/tickets` |
| GET | `/api/tickets` |
| GET | `/api/tickets/export.csv` |
| GET | `/api/tickets/{ticketId}` |
| PATCH | `/api/tickets/{ticketId}` |
| PATCH | `/api/tickets/{ticketId}/status` |
| POST | `/api/tickets/{ticketId}/comments` |

### Key Behaviors

- `X-User-Id` required for: ticket create, comment create, CSV export
- Invalid status transitions → **HTTP 409** `INVALID_STATUS_TRANSITION`
- `PATCH /api/tickets/{id}` rejects `status`, `createdBy`, `createdAt`, `updatedAt`
- List endpoint: search, filters, pagination (`page`, `pageSize`)
- CSV: formula-injection mitigation, comment count column

### Verification

```bash
cd src/backend && source .venv/bin/activate
alembic upgrade head
python -m app.scripts.seed
pytest ../../tests -q   # 40 passed
```

### Next Session (Suggested)

```
Implement M5 — Frontend Core UI per ui-flow.md:
- ActingUserContext + api/client.ts with X-User-Id
- Ticket list, create, detail pages
- Wire to /api/* endpoints
```

---

## Sessions

| Date | Milestone | Summary |
|------|-----------|---------|
| 2026-07-18 | M0 | Scaffold only |
| 2026-07-20 | M1–M4 | Core backend complete, 40 tests passing |
