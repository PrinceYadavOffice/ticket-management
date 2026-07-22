# Review Fixes

Track fixes applied in response to code review feedback.

| Review ID | Finding | Fix Applied | Files | Regression test |
|-----------|---------|-------------|-------|-----------------|
| CR-01 | PATCH validation returned HTTP 500 | Added `ValidationError` and `JSONDecodeError` exception handlers mapping to 422 | `src/backend/app/core/exceptions.py` | `test_blank_title_on_patch_returns_422`, `test_invalid_priority_on_patch_returns_422`, `test_malformed_json_on_patch_returns_422` |
| CR-02 | Comment form cleared before async submit finished | `await onSubmit`; clear on success only; parent rethrows | `CommentForm.tsx`, `TicketDetailPage.tsx` | `CommentForm.test.tsx` (3 tests) |
| CR-03 | Acting user selection overwritten after fetch | Functional `setState` preserves valid `prev` | `ActingUserContext.tsx` | Manual review; existing `App.test.tsx` |
| CR-04 | No DB rollback on exception | `db.rollback()` in `get_db` except block | `src/backend/app/core/database.py` | Existing service tests |
| CR-05 | Unsafe JSON parsing in API client | `parseJsonBody`, `toApiError`, `isApiErrorBody` | `src/frontend/src/api/client.ts` | `client.test.ts` (2 tests) |
| CR-06 | User fetch errors hidden | Error and empty-user UI in selector | `ActingUserSelector.tsx` | `App.test.tsx` |
| CR-07 | Stale tickets shown with list error | Clear tickets/total in catch | `TicketListPage.tsx` | — |
| CR-08 | Seed wrote invalid priority/status | Validate enums before insert | `src/backend/app/scripts/seed.py` | Seed idempotency (manual) |
| CR-09 | CSV download URL revoked too early | `setTimeout(..., 100)` before revoke | `TicketExportButton.tsx` | — |
| CR-10 | Dead `STATUS_ACTIONS` constant | Removed | `utils/constants.ts` | — |
| CR-11 | 500 handler did not log | `logger.exception` | `exceptions.py` | — |
| CR-12 | Mutable default on `ErrorBody.details` | `Field(default_factory=dict)` | `exceptions.py` | — |
| CR-13 | Misaligned transition test assertion | Updated mock error message | `TicketDetailPage.test.tsx` | Same file |

**Post-fix verification (2026-07-22):**

```
pytest tests -q          → 68 passed
npm test (frontend)      → 25 passed
npm run build (frontend) → success
```
