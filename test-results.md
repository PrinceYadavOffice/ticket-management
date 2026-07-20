# Test Results

## Latest Run

| Field | Value |
|-------|-------|
| Date | 2026-07-20 |
| Environment | macOS, Python 3.10.14 |
| Command | `cd src/backend && source .venv/bin/activate && pytest ../../tests -v` |
| Test database | Isolated SQLite file per test (`tmp_path/pytest_tickets.db`) |

### Backend (Pytest)

```
======================== 65 passed, 1 warning in 2.49s =========================
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

### Implementation defects found

None — all tests passed without code changes in this session.

### Frontend (Vitest)

Not run in this session.

---

## History

| Date | Backend | Frontend | Notes |
|------|---------|----------|-------|
| 2026-07-18 | N/A | 2 passed | Frontend scaffold |
| 2026-07-20 (AM) | 40 passed | N/A | Initial backend implementation |
| 2026-07-20 (PM) | **65 passed** | Not run | Comprehensive API + integration tests |
