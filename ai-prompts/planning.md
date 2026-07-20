# Planning Phase Prompts

## Session: 2026-07-18 — Initial Repository Scaffold

### User Request (Summary)

Create the initial structure and planning artifacts for an AI-assisted full-stack **Support Ticket Management System** with:

- **Stack:** React + TypeScript + Vite, FastAPI, SQLAlchemy, SQLite, Alembic, Pytest, Vitest + RTL
- **Entities:** User (seeded), Ticket, Comment (with specified fields)
- **Features:** CRUD-ish ticket ops, comments, search/filter, persistence, validation, CSV export, status state machine
- **Auth:** Optional — NOT in Core; use seeded user selector + `X-User-Id` header as acting-user context
- **Status transitions:** Open→In Progress, In Progress→Resolved, Resolved→Closed, Open→Cancelled, In Progress→Cancelled; all others rejected
- **Do not implement application features yet**

### Deliverables Created

1. Root planning documents (17 markdown files)
2. `src/backend/` — FastAPI scaffold with health endpoint, Alembic config, empty model/api/service packages
3. `src/frontend/` — Vite + React + TS scaffold with placeholder App and sample RTL test
4. `tests/` — Pytest conftest, health test, integration placeholder
5. `database/` — seed data, setup notes, migrations reference
6. `artifacts/prompt-history/TEMPLATE.md`
7. `ai-prompts/` — phase prompt stubs
8. `.gitignore`, `.env.example`
9. `.cursor/rules/` — project rules

### Completed Planning Docs (Full Content)

- `requirements-analysis.md` — FR/NFR, assumptions, PO questions, edge cases
- `acceptance-criteria.md` — measurable AC, Core vs Stretch, definition of done
- `implementation-plan.md` — milestones M0–M6, risks, dependencies

### Draft Planning Docs

- `api-contract.md`, `data-model.md`, `ui-flow.md`, `design-notes.md`, `test-strategy.md`

### Key Decisions Documented

| Topic | Decision |
|-------|----------|
| Acting user | `X-User-Id` header; explicitly NOT authentication |
| Status updates | Dedicated `PATCH /tickets/{id}/status` endpoint |
| User management | Seeded only; no CRUD in Core |
| CSV scope | Tickets where `createdBy` = acting user |
| Stretch | Auth, RBAC, pagination, CI/CD, etc. |

### Next Session Prompt (Suggested)

```
Implement M1 — Data Layer & Seeding:
- SQLAlchemy models for User, Ticket, Comment
- Initial Alembic migration
- Seed script from database/seed-data/users.json
- Update data-model.md if schema differs
```

### Prompt History Entry

Logged at: `artifacts/prompt-history/2026-07-18-initial-scaffold.md`

---

## Reusable Planning Prompt Template

```
Context: Support Ticket Management System (see README.md, requirements-analysis.md)

Task: [PLANNING TASK]

Constraints:
- Core vs Stretch per acceptance-criteria.md
- Acting-user via X-User-Id, not auth
- Status state machine per api-contract.md

Output: Update [TARGET DOCS] only; do not implement features unless asked.
```
