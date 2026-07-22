# Acceptance Criteria

## Support Ticket Management System

Measurable criteria for declaring Core complete. Each item should be verifiable manually or via automated tests.

---

## 1. Acting-User Context

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-01 | Frontend displays a dropdown of seeded users | Manual: selector visible on load |
| AC-02 | Changing user updates `X-User-Id` on subsequent API calls | Manual / network tab |
| AC-03 | Documentation states this is acting-user context, not auth | README, api-contract, design-notes |
| AC-04 | Missing `X-User-Id` returns error with message | API test |
| AC-05 | Invalid `X-User-Id` returns error with message | API test |

---

## 2. Tickets — Create & List

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-10 | `POST /tickets` creates ticket with Open status | API test |
| AC-11 | `createdBy` matches `X-User-Id` | API test |
| AC-12 | `createdAt` and `updatedAt` populated | API test |
| AC-13 | `GET /tickets` returns list of tickets | API test + UI |
| AC-14 | Empty required fields rejected with `422` and field errors | API test |
| AC-15 | Frontend shows validation errors from API | UI test / manual |

---

## 3. Tickets — Detail & Update

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-20 | `GET /tickets/{id}` returns ticket with comments | API test |
| AC-21 | Non-existent ticket returns `404` | API test |
| AC-22 | `PATCH /tickets/{id}` updates title, description, priority, assignee | API test |
| AC-23 | `updatedAt` changes after update | API test |
| AC-24 | Invalid assignee rejected | API test |
| AC-25 | Frontend detail view shows all ticket fields | Manual / component test |

---

## 4. Comments

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-30 | `POST /tickets/{id}/comments` adds comment | API test |
| AC-31 | Comment records `createdBy` and `createdAt` | API test |
| AC-32 | Comments appear on ticket detail | API + UI |
| AC-33 | Comment on missing ticket returns `404` | API test |
| AC-34 | Empty message rejected | API test |

---

## 5. Status State Machine

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-40 | Open → In Progress succeeds | Integration test |
| AC-41 | In Progress → Resolved succeeds | Integration test |
| AC-42 | Resolved → Closed succeeds | Integration test |
| AC-43 | Open → Cancelled succeeds | Integration test |
| AC-44 | In Progress → Cancelled succeeds | Integration test |
| AC-45 | Open → Resolved fails | Integration test |
| AC-46 | Closed → Open fails | Integration test |
| AC-47 | Cancelled → In Progress fails | Integration test |
| AC-48 | Invalid transition returns consistent error shape | Integration test |
| AC-49 | UI reflects status after transition | Manual |

---

## 6. Search & Filter

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-50 | Filter by status returns matching tickets only | API test |
| AC-51 | Filter by priority returns matching tickets only | API test |
| AC-52 | Search by keyword matches title or description | API test |
| AC-53 | Frontend filter UI updates list | Manual / component test |
| AC-54 | No matches returns empty array with `200` | API test |

---

## 7. CSV Export

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-60 | Export endpoint returns `text/csv` | API test |
| AC-61 | CSV contains only tickets where `createdBy` = acting user | API test |
| AC-62 | CSV includes header row | API test |
| AC-63 | Frontend triggers download | Manual |
| AC-64 | User with no tickets gets headers-only CSV | API test |

---

## 8. Persistence

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-70 | Tickets survive backend restart | Manual / integration |
| AC-71 | Comments survive backend restart | Manual / integration |
| AC-72 | Alembic migrations apply cleanly on fresh DB | CI / manual |

---

## 9. Frontend Quality

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-80 | Loading states shown during API calls | Manual |
| AC-81 | API errors displayed in user-friendly form | Manual / component test |
| AC-82 | App builds without TypeScript errors | `npm run build` |
| AC-83 | Core flows navigable without console errors | Manual |

---

## 10. Test Coverage (Minimum)

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-90 | Pytest suite passes | `pytest` |
| AC-91 | Integration tests cover all valid status transitions | Test file review |
| AC-92 | Integration tests cover representative invalid transitions | Test file review |
| AC-93 | Vitest suite passes | `npm test` |
| AC-94 | At least one RTL test per major view (list, detail, create) | Test file review | **Partial** — list via `TicketList.test.tsx`, detail via `TicketDetailPage.test.tsx`, create via `TicketForm.test.tsx` (no `TicketCreatePage.test.tsx`) |

---

## Core vs Stretch Boundaries

### Core (Must Have)

All acceptance criteria **AC-01 through AC-94** above, plus:

- Entities: User (seeded), Ticket, Comment
- Full status state machine enforcement on backend
- `X-User-Id` acting-user context
- SQLite persistence with Alembic
- Backend validation + frontend error display
- CSV export for current user's created tickets
- Integration tests for status transitions
- Planning artifacts in repo root

### Stretch (Nice to Have — Not Required for Core Sign-off)

| ID | Feature | Notes |
|----|---------|-------|
| ST-01 | ~~Pagination on ticket list~~ | **Implemented in Core** — `page`/`pageSize` API + UI pagination |
| ST-02 | Role-based permissions | Enforce Agent vs Admin |
| ST-03 | Ticket assignment notifications | Email or toast |
| ST-04 | Optimistic locking | `version` field on Ticket |
| ST-05 | Dark mode | UI theme toggle |
| ST-06 | Docker Compose one-command start | DevOps |
| ST-07 | GitHub Actions CI | Lint, test, build |
| ST-08 | OpenAPI Swagger UI polish | Custom branding |
| ST-09 | Ticket history / audit log | Status change log |
| ST-10 | Reopen closed tickets | New state machine rules |

**Rule:** Stretch items must not block Core delivery. Implement only after all Core AC items pass.

---

## Definition of Done (Core)

1. All Core acceptance criteria pass (manual + automated).
2. `requirements-analysis.md`, `acceptance-criteria.md`, `implementation-plan.md` reflect implemented behavior.
3. `api-contract.md` and `data-model.md` match implementation.
4. `test-results.md` documents latest test run.
5. `candidate-info.md` placeholders replaced by candidate.
6. No critical bugs in primary user flows (create → list → detail → comment → status change → export).
