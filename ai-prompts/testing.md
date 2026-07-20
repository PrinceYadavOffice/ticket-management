# Testing Phase Prompts

## Purpose

Write and run backend/frontend tests; record results in `test-results.md`.

---

## Session: 2026-07-20 — Comprehensive Backend Test Suite

### User Request (Summary)

Review backend implementation. Create meaningful API and integration tests with Pytest and separate test database. Cover users, ticket CRUD, list/filter/pagination, state machine (valid + invalid + side effects), comments, CSV export. Run suite, fix defects, update docs.

### Test Infrastructure Changes

| Change | File |
|--------|------|
| Isolated file-based SQLite per test | `tests/conftest.py` (`tmp_path/pytest_tickets.db`) |
| Shared helpers | `tests/helpers.py` |
| Reorganized test modules | `tests/backend/*.py`, `tests/integration/*.py` |
| Removed monolithic file | Deleted `tests/backend/test_tickets.py` |

### New Test Files

- `test_ticket_create.py` — 9 tests
- `test_ticket_list.py` — 8 tests
- `test_ticket_detail_update.py` — 6 tests
- `test_comments.py` — 6 tests
- `test_export.py` — 9 tests (incl. parametrized formula injection)
- `test_status_transitions.py` — 15 integration tests (expanded)

### Results (Executed)

```
cd src/backend && source .venv/bin/activate && pytest ../../tests -v
65 passed, 1 warning in 2.49s
```

### Defects Fixed

None required — implementation passed all new tests without changes.

### Documentation Updated

- `test-strategy.md` v1.2
- `test-results.md`
- `debugging-notes.md`
- `ai-prompts/testing.md` (this file)
- `ai-prompts/debugging.md`

---

## Template

```
Context: Support Ticket Management System

Read: test-strategy.md, acceptance-criteria.md

Task: [TEST TASK]

Required:
- Use isolated test DB (conftest tmp_path)
- Use assert_error() for error envelope checks
- Reload DB state to verify transitions

Output: Test files + update test-results.md with actual run output
```

## Sessions

| Date | Suite | Result |
|------|-------|--------|
| 2026-07-20 | Backend Pytest | **65 passed**, 0 failed |
