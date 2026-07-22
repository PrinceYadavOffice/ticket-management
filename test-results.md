# Test Results

## Latest Run

| Field | Value |
|-------|-------|
| Date | 2026-07-22 |
| Environment | macOS, Python 3.10.14, Node.js (Vite 5) |
| Backend command | `pytest tests -q` (from repo root) |
| Frontend command | `cd src/frontend && npm test && npm run build` |
| Test database | Isolated SQLite file per test (`tmp_path/pytest_tickets.db`) |

### Backend (Pytest)

```
65 passed, 1 warning in 4.54s
```

| Suite | Passed | Failed | Skipped |
|-------|--------|--------|---------|
| `tests/backend/test_comments.py` | 6 | 0 | 0 |
| `tests/backend/test_export.py` | 9 | 0 | 0 |
| `tests/backend/test_health.py` | 1 | 0 | 0 |
| `tests/backend/test_status_machine.py` | 9 | 0 | 0 |
| `tests/backend/test_ticket_create.py` | 9 | 0 | 0 |
| `tests/backend/test_ticket_detail_update.py` | 6 | 0 | 0 |
| `tests/backend/test_ticket_list.py` | 8 | 0 | 0 |
| `tests/backend/test_users.py` | 2 | 0 | 0 |
| `tests/integration/test_status_transitions.py` | 15 | 0 | 0 |
| **Total** | **65** | **0** | **0** |

**Warning:** Starlette deprecation about `httpx` vs `httpx2` (test client only; no test failures).

### Frontend (Vitest + TypeScript + Vite build)

```
Test Files  8 passed (8)
     Tests  20 passed (20)

tsc --noEmit — no errors
vite build — success (dist/ produced)
```

| Test file | Tests | Coverage focus |
|-----------|-------|----------------|
| `api/tickets.test.ts` | 4 | `X-User-Id` header, `buildQuery` filter params |
| `components/tickets/TicketList.test.tsx` | 1 | Ticket list table rendering |
| `components/tickets/TicketForm.test.tsx` | 4 | Required field validation, API error display |
| `components/tickets/TicketFilters.test.tsx` | 1 | Filter → API param mapping |
| `components/tickets/TicketStatusActions.test.tsx` | 5 | Transition visibility, terminal statuses, rejected transition |
| `components/common/ErrorAlert.test.tsx` | 1 | Backend error message display |
| `pages/TicketDetailPage.test.tsx` | 3 | Ticket edit, comment submission, rejected transition |
| `App.test.tsx` | 1 | Acting-user disclaimer in shell |

### Implementation defects found

None in this session — all tests and builds passed after minor test assertion fixes (`findByDisplayValue`, status button wait).

---

## History

| Date | Backend | Frontend | Notes |
|------|---------|----------|-------|
| 2026-07-18 | N/A | 2 passed | Frontend scaffold |
| 2026-07-20 (AM) | 40 passed | N/A | Initial backend implementation |
| 2026-07-20 (PM) | **65 passed** | Not run | Comprehensive API + integration tests |
| 2026-07-22 | **65 passed** | **20 passed**, build OK | M5 Core frontend complete |
