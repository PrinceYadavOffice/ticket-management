# Reflection

Post-project reflection for the Support Ticket Management System submission.

---

## What Was Built

A complete **Core** full-stack ticket management system:

- **Backend:** FastAPI REST API with 9 endpoints, SQLAlchemy models, Alembic migration, idempotent seed script, status state machine, CSV export with formula-injection mitigation
- **Frontend:** React + TypeScript + Vite SPA with ticket list (search/filter/pagination), create page, detail page (edit, status actions, comments), acting-user selector
- **Tests:** 68 backend (Pytest) + 25 frontend (Vitest/RTL)
- **Documentation:** Planning, design, API contract, UI flow, test strategy, review artifacts, AI usage log

Stretch features (real auth, RBAC, Docker, CI) were intentionally not built.

---

## How AI Was Used

Cursor Agent mode across **~7 major sessions** from scaffold through submission audit:

| Phase | AI role |
|-------|---------|
| Planning | Generated repo structure and 17+ planning markdown files |
| Design | Produced architecture, API contract, data model, UI flow |
| Backend | Implemented services, routes, migration, seed, initial tests |
| Frontend | Built full UI, API client, context, component tests |
| Testing | Expanded backend suite; wrote focused frontend tests |
| Review | Live verification, classified findings, applied fixes |
| Documentation | README, compliance checklist, submission artifacts |

Human directed **what** to build (milestones, Core scope, state machine rules). AI generated **how** (file structure, boilerplate, test cases) with human verification via test runs.

---

## Where AI Helped Most

1. **Rapid scaffolding** — entire repo layout, FastAPI/React project setup, Alembic config in one session
2. **Boilerplate consistency** — Pydantic schemas, error envelope, API client pattern
3. **Test expansion** — parametrized export tests, status transition integration tests
4. **Cross-file implementation** — wiring frontend pages to API contract across many components
5. **Review breadth** — systematic curl matrix and code exploration in parallel

---

## What AI Got Wrong or Overcomplicated

| Issue | What happened |
|-------|---------------|
| PATCH returns 500 | AI used manual `model_validate` without mapping `ValidationError` to 422 — caught in review |
| Frontend test assertions | `findByText('Open')` failed when title was in input value — fixed to `findByDisplayValue` |
| Comment form race | Cleared textarea before async submit completed |
| Over-suggested refactors | Proposed NOT_FOUND helpers, abort controllers, microservices — rejected as unnecessary |
| Test count drift | README said 65/20 tests while actual was 68/25 — fixed in audit |
| localhost "not working" | Servers simply weren't running — not a code bug |

---

## What Was Changed or Rejected

**Accepted:** Exception handlers for PATCH validation, comment form async fix, acting-user race fix, API client safe JSON parsing, 13 review fixes total.

**Rejected:**
- Microservices, Kubernetes, real authentication
- Major UI redesign
- List-fetch `AbortController` (complexity vs benefit)
- Removing duplicate unassigned filter UX
- Dead code cleanup (`CommentResponse`) without behavior impact

---

## How AI Output Was Validated

| Method | Used for |
|--------|----------|
| `pytest tests -q` | All backend behavior |
| `npm test` + `npm run build` | Frontend behavior + types |
| `curl` live API matrix | Error codes, CORS, CSV |
| Clean DB workflow | migrate → seed ×2 → tests |
| `git ls-files` | No secrets/generated files tracked |
| Code review checklist | Architecture, security basics |

**Rule:** No success claim without command output in the same session.

---

## Technical Trade-offs

| Decision | Trade-off |
|----------|-----------|
| SQLite | Simple local dev; not production-scale concurrency |
| `X-User-Id` header (no auth) | Fast Core delivery; client can spoof acting user |
| String enums in DB | Flexible storage; no DB-level enum constraint |
| Manual PATCH body parsing | Supports `assignedTo: null` + forbidden fields; required extra exception handlers |
| Component vs page tests | Faster tests; AC-94 partially met for create page |
| localStorage for acting user | Persists selection; not cross-tab sync guaranteed |

---

## Future Improvements

1. Real authentication and role-based permissions (Stretch)
2. GitHub Actions CI (lint, test, build on push)
3. `TicketCreatePage` page-level RTL test
4. Docker Compose for one-command dev start
5. Request abort/sequence guard on ticket list fetches
6. OpenAPI client generation from contract
7. E2E tests (Playwright) for full browser flows

---

## Reusable Prompts and Cursor Rules

| Asset | Location | Purpose |
|-------|----------|---------|
| Planning template | `ai-prompts/planning.md` | Milestone kickoff |
| Design template | `ai-prompts/design.md` | Pre-implementation design |
| Implementation template | `ai-prompts/implementation.md` | Feature coding sessions |
| Testing template | `ai-prompts/testing.md` | Test expansion |
| Debugging template | `ai-prompts/debugging.md` | Bug investigation |
| Code review template | `ai-prompts/code-review.md` | Quality review |
| Documentation template | `ai-prompts/documentation.md` | Doc alignment |
| Prompt history template | `artifacts/prompt-history/TEMPLATE.md` | Per-session log |
| Cursor rules | `.cursor/rules/` | Persistent constraints |
| Cursor workflow | `tool-specific/cursor-workflow/README.md` | Branch naming, agent hints |

**Effective prompt pattern:** "Read X first. Implement Y per api-contract. Run tests. Update Z docs. Do not add Stretch features."

---

## Time Breakdown (Approximate)

| Phase | Hours (est.) |
|-------|----------------|
| Planning & scaffold | 2–3 |
| Design | 2 |
| Backend implementation | 4–6 |
| Backend testing | 2 |
| Frontend implementation | 4–6 |
| Quality review & fixes | 2–3 |
| Documentation & audit | 2 |
| **Total** | **~18–24** (candidate should confirm in `candidate-info.md`) |
