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
Stretch goals: real authentication, role-based UI, deployment automation.
```

---

## Session: 2026-07-22 — Core Frontend (M5)

### User Request (Summary)

Implement complete Core frontend per `ui-flow.md` and `api-contract.md`: ticket list, create, detail pages; acting-user selector with `localStorage`; all required components and states; focused frontend tests; run tsc/test/build.

### Implemented

| Area | Files |
|------|-------|
| API layer | `api/client.ts`, `api/types.ts`, `api/tickets.ts` |
| Context | `context/ActingUserContext.tsx` |
| Layout | `components/layout/AppLayout.tsx`, `components/users/ActingUserSelector.tsx` |
| Tickets | `TicketList`, `TicketFilters`, `TicketForm`, `TicketStatusActions`, `TicketExportButton` |
| Comments | `CommentList`, `CommentForm` |
| Common | `ErrorAlert`, `LoadingSpinner`, `EmptyState`, `NotFoundState` |
| Pages | `TicketListPage`, `TicketCreatePage`, `TicketDetailPage` |
| App | `App.tsx`, `App.css`, `utils/constants.ts` |
| Tests | 8 test files, 20 tests (Vitest + RTL) |

### Key Behaviors

- `X-User-Id` sent on: ticket create, comment create, CSV export (via `requireActingUser` / explicit `actingUserId`)
- Acting user persisted in `localStorage` key `actingUserId`
- Status buttons driven by `allowedStatusTransitions` from API; 409 errors shown without incorrect status
- Frontend validation for required fields; backend `error.details.fields` mapped to form errors
- Loading/disabled states on all mutations; duplicate submission guarded

### Verification

```bash
cd src/frontend
npm test        # 20 passed
npm run build   # tsc + vite build success
```

---

## Sessions

| Date | Milestone | Summary |
|------|-----------|---------|
| 2026-07-18 | M0 | Scaffold only |
| 2026-07-20 | M1–M4 | Core backend complete, 40 tests passing |
| 2026-07-22 | M5 | Core frontend complete, 20 frontend tests passing |
