# Test Results

## Latest Run

| Field | Value |
|-------|-------|
| Date | 2026-07-22 |
| Environment | macOS, Python 3.10.14, Node.js (Vite 5) |
| Review | Submission documentation audit (clean verification) |
| Backend command | `pytest tests -q` (repo root) |
| Frontend command | `cd src/frontend && npm test && npm run build` |
| Test database | Isolated SQLite per test (`tmp_path/pytest_tickets.db`) |

### Backend (Pytest)

```
68 passed, 1 warning in 2.32s
```

| Suite | Passed | Failed | Skipped |
|-------|--------|--------|---------|
| `tests/backend/test_comments.py` | 6 | 0 | 0 |
| `tests/backend/test_export.py` | 9 | 0 | 0 |
| `tests/backend/test_health.py` | 1 | 0 | 0 |
| `tests/backend/test_status_machine.py` | 9 | 0 | 0 |
| `tests/backend/test_ticket_create.py` | 9 | 0 | 0 |
| `tests/backend/test_ticket_detail_update.py` | **9** | 0 | 0 |
| `tests/backend/test_ticket_list.py` | 8 | 0 | 0 |
| `tests/backend/test_users.py` | 2 | 0 | 0 |
| `tests/integration/test_status_transitions.py` | 15 | 0 | 0 |
| **Total** | **68** | **0** | **0** |

**New in review:** 3 PATCH validation regression tests in `test_ticket_detail_update.py`.

**Warning:** Starlette deprecation about `httpx` vs `httpx2` (test client only).

### Frontend (Vitest + TypeScript + Vite build)

```
Test Files  10 passed (10)
     Tests  25 passed (25)

tsc --noEmit — no errors
vite build — success
```

| Test file | Tests | Coverage focus |
|-----------|-------|----------------|
| `api/tickets.test.ts` | 4 | `X-User-Id` header, `buildQuery` |
| `api/client.test.ts` | 2 | Network error, malformed JSON |
| `components/tickets/TicketList.test.tsx` | 1 | Table rendering |
| `components/tickets/TicketForm.test.tsx` | 4 | Validation, API errors |
| `components/tickets/TicketFilters.test.tsx` | 1 | Filter param mapping |
| `components/tickets/TicketStatusActions.test.tsx` | 5 | Transitions, terminal, rejected |
| `components/common/ErrorAlert.test.tsx` | 1 | Error display |
| `components/comments/CommentForm.test.tsx` | 3 | Blank validation, retry, success clear |
| `pages/TicketDetailPage.test.tsx` | 3 | Edit, comment, rejected transition |
| `App.test.tsx` | 1 | Acting-user disclaimer |

### Live verification (review session)

| Check | Result |
|-------|--------|
| `pip install`, `npm ci` | Pass |
| `alembic upgrade head` | Pass |
| Seed ×2 (idempotent) | Pass |
| CORS preflight | Pass |
| Full API error matrix (curl) | Pass (after CR-01 fix) |
| DB persistence after restart | Pass |

### Latest audit (2026-07-22 submission)

```
rm data/tickets.db
pip install -r requirements.txt && npm ci
alembic upgrade head && python -m app.scripts.seed (×2)
pytest tests -q          → 68 passed
npm test                 → 25 passed
npm run build            → success
curl health/users/tickets/export → 200
git ls-files secrets     → none tracked
```

---

## History

| Date | Backend | Frontend | Notes |
|------|---------|----------|-------|
| 2026-07-18 | N/A | 2 passed | Frontend scaffold |
| 2026-07-20 (AM) | 40 passed | N/A | Initial backend |
| 2026-07-20 (PM) | 65 passed | Not run | Comprehensive backend tests |
| 2026-07-22 (AM) | 65 passed | 20 passed | M5 frontend complete |
| 2026-07-22 (PM) | **68 passed** | **25 passed**, build OK | Core-quality review + fixes |
| 2026-07-22 (audit) | **68 passed** | **25 passed**, build OK | Submission documentation audit |
