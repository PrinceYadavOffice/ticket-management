# Design Phase Prompts

## Purpose

Refine API contract, data model, UI flows, design notes, and test strategy before implementation.

## Template

```
Context: Support Ticket Management System

Review: api-contract.md, data-model.md, ui-flow.md, design-notes.md, test-strategy.md

Task: [DESIGN TASK]

Constraints:
- Status transitions per requirements-analysis.md
- X-User-Id acting-user context (not auth)
- SQLite + SQLAlchemy snake_case DB, camelCase API
- Error envelope: { error: { code, message, details } }
- Status changes only via PATCH /tickets/{id}/status
- Priority: Low, Medium, High, Critical

Output: Update design docs only; do not implement features unless asked.
```

---

## Session: 2026-07-20 — Complete Design Artifacts

### User Request (Summary)

Review `requirements-analysis.md`, `acceptance-criteria.md`, and `implementation-plan.md`. Complete design documents without implementing application features:

- `design-notes.md` — architecture, modules, trade-offs
- `data-model.md` — tables with `assigned_to_user_id`, `created_by_user_id`
- `api-contract.md` — full endpoint specs with error envelope
- `ui-flow.md` — component structure and user journeys
- `test-strategy.md` — test layers and case inventory

Key specifications:

- Priority enum includes **Critical**
- Consistent error format: `{ error: { code, message, details } }`
- State machine in dedicated `services/status_machine.py`
- `PATCH /tickets/{id}` must not allow status updates
- Document every endpoint: method, path, purpose, request, response, validation, status codes, errors

### Deliverables

| Artifact | Version | Key content |
|----------|---------|-------------|
| `design-notes.md` | 1.0 | 3-tier architecture, backend/frontend module trees, X-User-Id flow, validation/error strategies, search/filter, CSV, trade-offs |
| `data-model.md` | 1.0 | ERD, three tables, enums, indexes, API↔DB mapping |
| `api-contract.md` | 1.0 | 9 endpoints fully specified, error codes, `allowedStatusTransitions` on detail |
| `ui-flow.md` | 1.0 | Routes, component matrix, sequence diagrams, error/loading states |
| `test-strategy.md` | 1.0 | 5 layers, 60+ test case IDs, error envelope helper |

### Design Decisions Made

| Topic | Decision |
|-------|----------|
| Error format | `{ error: { code, message, details } }` on all errors |
| DB FK columns | `assigned_to_user_id`, `created_by_user_id` |
| Priority | Low, Medium, High, **Critical** |
| Status update | Only `PATCH /tickets/{ticketId}/status` via `status_machine.py` |
| GET /users header | Not required (bootstrap for selector) |
| GET /tickets/export | Registered before `/{ticketId}` route |
| Ticket detail | Includes `allowedStatusTransitions` for UI buttons |
| Filter logic | AND combination; `unassigned=true` param |
| CSV scope | `created_by_user_id` = acting user |
| Comments | Do not bump ticket `updatedAt` |

### Alignment with Planning Docs

- Requirements FR-S-* and FR-T-* — covered in API contract and data model
- Acceptance criteria AC-40–48 — mapped to IT-S-* integration tests
- Implementation plan M1–M5 — design docs ready for each milestone

### Gaps / Follow-up for Implementation

1. Update `requirements-analysis.md` assumption A-03 to include Critical (optional doc sync)
2. Implement `core/dependencies.py` (`get_acting_user`)
3. Implement `core/exceptions.py` (error envelope handlers)
4. M1: models matching `data-model.md` column names exactly

### Next Session Prompt (Suggested)

```
Implement M1 — Data Layer & Seeding per data-model.md:
- SQLAlchemy models (users, tickets, comments)
- Alembic 001_initial migration
- Seed script from database/seed-data/users.json
Do not implement API routes yet.
```

### Prompt History Entry

`artifacts/prompt-history/2026-07-20-design-complete.md` (candidate may create from TEMPLATE)

---

## Sessions

| Date | Task | Artifacts Updated |
|------|------|-------------------|
| 2026-07-20 | Complete design artifacts | design-notes, data-model, api-contract, ui-flow, test-strategy |
