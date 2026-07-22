# Code Review Notes

**Review date:** 2026-07-22  
**Scope:** Core full-stack (backend M1–M4, frontend M5)  
**Reviewer:** AI-assisted senior review  
**Verification:** Clean install, migrate, double-seed, live API curls, 68 backend + 25 frontend tests, production build

---

## Review Checklist

- [x] Status machine logic only in backend service
- [x] `X-User-Id` validated on protected routes
- [x] No secrets in code or commits
- [x] API responses match `api-contract.md` (after fixes)
- [x] Error shapes consistent (after fixes)
- [x] Tests cover invalid status transitions
- [x] Frontend documents acting-user disclaimer
- [x] CSV export scoped to `createdBy` = acting user

---

## Verification Summary

| Check | Result |
|-------|--------|
| `pip install -r requirements.txt` | Pass |
| `npm ci` | Pass |
| `alembic upgrade head` | Pass |
| `python -m app.scripts.seed` (×2) | Pass — idempotent (4 users, 6 tickets, 6 comments) |
| Backend startup (`uvicorn`) | Pass |
| Frontend startup (`npm run dev`) | Pass |
| CORS preflight (`OPTIONS` from `localhost:5173`) | Pass (200) |
| Ticket CRUD, filters, status, comments, CSV | Pass (live curls) |
| DB persistence after backend restart | Pass (ticket #7 retained) |
| Backend tests | **68 passed** |
| Frontend tests | **25 passed** |
| Frontend production build | Pass |

---

## Findings

| ID | Severity | Location | Problem | Impact | Recommended fix | Status | Reason |
|----|----------|----------|---------|--------|-----------------|--------|--------|
| CR-01 | **High** | `src/backend/app/api/tickets.py` + `app/core/exceptions.py` | `PATCH /api/tickets/{id}` uses manual `model_validate`; Pydantic `ValidationError` and malformed JSON hit global `Exception` handler → **HTTP 500** instead of **422** | Contract violation; frontend cannot show field errors on ticket edit | Register handlers for `ValidationError` and `JSONDecodeError` | **Changed** | Confirmed via curl before fix |
| CR-02 | **High** | `src/frontend/src/components/comments/CommentForm.tsx` | Cleared textarea immediately after `onSubmit`, before async API completed | User loses comment text on failed post | `await onSubmit`; clear only on success; rethrow from parent | **Changed** | Real UX bug |
| CR-03 | **High** | `src/frontend/src/context/ActingUserContext.tsx` | `fetchUsers` completion always called `setCurrentUserIdState(initialId)`, overwriting in-flight user selection | Wrong acting user sent on create/comment/export | Preserve `prev` if still valid in user list | **Changed** | Race on slow network |
| CR-04 | **Medium** | `src/backend/app/core/database.py` | `get_db()` closed session without `rollback()` on exception | Partial writes could leave session dirty | `except: db.rollback(); raise` | **Changed** | Standard SQLAlchemy pattern |
| CR-05 | **Medium** | `src/frontend/src/api/client.ts` | `response.json()` on all responses; malformed bodies threw `SyntaxError` | Network/backend glitches crash error handling | Safe parse with `toApiError` fallback | **Changed** | Defensive Core quality |
| CR-06 | **Medium** | `src/frontend/src/components/users/ActingUserSelector.tsx` | User fetch errors not shown | Empty/broken selector with no recovery | Render `error` and empty-user states | **Changed** | Operational clarity |
| CR-07 | **Medium** | `src/frontend/src/pages/TicketListPage.tsx` | On fetch error, stale tickets remained visible | Misleading UI alongside error alert | Clear `tickets` and `total` on error | **Changed** | Data integrity in UI |
| CR-08 | **Medium** | `src/backend/app/scripts/seed.py` | Raw JSON priority/status written without enum check | Bad seed data could corrupt DB | Validate `TicketPriority` / `TicketStatus` before insert | **Changed** | Fail-safe seeding |
| CR-09 | **Medium** | `src/frontend/src/components/tickets/TicketExportButton.tsx` | `URL.revokeObjectURL` immediately after `click()` | Download may fail in some browsers | Defer revoke with `setTimeout` | **Changed** | Known browser quirk |
| CR-10 | **Low** | `src/frontend/src/utils/constants.ts` | `STATUS_ACTIONS` exported but unused | Dead code; risk of frontend duplicating state machine | Remove; rely on `allowedStatusTransitions` from API | **Changed** | Backend is source of truth |
| CR-11 | **Low** | `src/backend/app/core/exceptions.py` | Unhandled exceptions returned 500 with no server log | Harder production debugging | `logger.exception` in catch-all handler | **Changed** | Ops visibility |
| CR-12 | **Low** | `src/backend/app/core/exceptions.py` | `ErrorBody.details` mutable default `{}` | Shared state risk across instances | `Field(default_factory=dict)` | **Changed** | Pydantic best practice |
| CR-13 | **Low** | `src/frontend/src/pages/TicketDetailPage.test.tsx` | Transition test asserted wrong error message | Weak regression signal | Align mock message with clicked transition | **Changed** | Test accuracy |
| CR-14 | **Low** | `src/backend/app/services/ticket_service.py` | Repeated NOT_FOUND blocks | Maintainability noise | Extract small helper | **Rejected** | No behavior change; out of review scope |
| CR-15 | **Low** | `src/backend/app/schemas/comment.py` | `CommentResponse` unused | Dead code | Remove or wire up | **Rejected** | Harmless; avoid unrelated cleanup |
| CR-16 | **Low** | `src/frontend/src/pages/TicketListPage.tsx` | No abort/sequence guard on list fetches | Stale response could overwrite newer filters | Add `AbortController` or request id | **Rejected** | Adds complexity; rare in Core demo |
| CR-17 | **Low** | `src/backend/app/schemas/ticket.py` | `TicketStatusUpdate` lacks `extra="forbid"` | Unknown keys silently ignored | Add `extra="forbid"` | **Rejected** | Low risk; status body is single field |
| CR-18 | **Rejected suggestion** | Architecture | Introduce microservices / K8s / real auth | N/A | N/A | **Rejected** | Stretch scope per requirements |
| CR-19 | **Rejected suggestion** | Frontend | Large UI redesign or new state library | N/A | N/A | **Rejected** | Unnecessary complexity |
| CR-20 | **Rejected suggestion** | `src/frontend/src/components/tickets/TicketFilters.tsx` | Duplicate unassigned UX (checkbox + select option) | Minor redundancy | Remove checkbox | **Rejected** | Both work; refactor not required for Core |

---

## Validation & Error Matrix (verified)

| Scenario | Expected | Observed |
|----------|----------|----------|
| Missing `X-User-Id` (create/export) | 401 `MISSING_ACTING_USER` | Pass |
| Invalid `X-User-Id` | 401 `ACTING_USER_NOT_FOUND` | Pass |
| Blank title (create) | 422 field error | Pass |
| Blank description (create) | 422 field error | Pass |
| Invalid priority (create) | 422 field error | Pass |
| Invalid assignee (create) | 422 field error | Pass |
| Blank comment | 422 field error | Pass |
| Invalid status value | 422 field error | Pass |
| Invalid state transition | 409 `INVALID_STATUS_TRANSITION` | Pass |
| Missing ticket | 404 `NOT_FOUND` | Pass |
| Malformed JSON body (PATCH) | 422 (was 500 — **fixed**) | Pass after fix |
| Blank title (PATCH) | 422 (was 500 — **fixed**) | Pass after fix |
| Frontend network failure | `NetworkError` in client | Pass (unit test) |
| CSV without user | 401 | Pass |
| CSV with valid user | 200 + CSV body | Pass |

---

## Senior Review Themes

| Area | Assessment |
|------|------------|
| **Maintainability** | Good for Core scope; services are readable; some duplication in schemas/services acceptable |
| **Separation of concerns** | API thin; business logic in services; status machine isolated |
| **Type safety** | Strong on API boundaries; ORM uses strings for enums (acceptable for SQLite Core) |
| **State machine** | Correctly backend-only (`status_machine.py`); frontend uses `allowedStatusTransitions` |
| **Transactions** | Single-commit per operation; rollback added on session errors |
| **Migrations** | Clean initial migration with indexes and FKs |
| **Error consistency** | Uniform envelope; PATCH validation gap fixed |
| **CSV safety** | Formula-prefix mitigation tested |
| **Accessibility** | Labels on main forms; acting-user error states added; room for pagination `aria-label`s (low priority) |
| **Frontend state** | Context + local page state appropriate for Core; no over-engineering |
| **Security basics** | No secrets; input validation; acting-user header; no auth by design |
| **Configuration** | `.env` optional; sensible defaults |
| **Test quality** | Good backend coverage; frontend focused tests expanded (+5 cases) |

---

## Real Bug Record

See `debugging-notes.md` — entry **2026-07-22 — PATCH ticket validation returns 500**.
