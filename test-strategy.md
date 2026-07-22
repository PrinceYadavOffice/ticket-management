# Test Strategy

**Version:** 1.2  
**Last Updated:** 2026-07-22  
**Status:** Implemented — 68 backend + 25 frontend tests passing

---

## 1. Goals

- Verify all Core backend acceptance criteria
- Prove status machine correctness with integration tests that check DB state
- Use an **isolated test database** — never `data/tickets.db`

---

## 2. Test Database

| Aspect | Approach |
|--------|----------|
| Engine | SQLite file per test via `tmp_path / "pytest_tickets.db"` |
| Isolation | `Base.metadata.create_all` before each test; file in pytest temp dir |
| Production DB | Never touched by tests |
| Fixtures | `tests/conftest.py` |

```python
@pytest.fixture
def test_db_path(tmp_path):
    return tmp_path / "pytest_tickets.db"
```

---

## 3. Test Layout

```
tests/
├── conftest.py              # DB engine, session, client, seeded users
├── helpers.py               # acting_user_header, assert_error, factories
├── backend/
│   ├── test_health.py
│   ├── test_users.py
│   ├── test_ticket_create.py
│   ├── test_ticket_list.py
│   ├── test_ticket_detail_update.py
│   ├── test_comments.py
│   ├── test_export.py
│   └── test_status_machine.py   # pure domain unit tests
└── integration/
    └── test_status_transitions.py
```

---

## 4. Coverage Matrix

### Users

| Test | File |
|------|------|
| Seeded users listable | `test_users.py` |
| Required fields present | `test_users.py` |

### Ticket creation

| Test | File |
|------|------|
| Successful creation | `test_ticket_create.py` |
| Missing X-User-Id | `test_ticket_create.py` |
| Invalid X-User-Id (non-integer, not found) | `test_ticket_create.py` |
| Blank title / description | `test_ticket_create.py` |
| Invalid priority / assignee | `test_ticket_create.py` |
| Persistence | `test_ticket_create.py` |

### Ticket list

| Test | File |
|------|------|
| Returns persisted tickets | `test_ticket_list.py` |
| Title + description search | `test_ticket_list.py` |
| Status / priority / assignee / creator filters | `test_ticket_list.py` |
| Pagination | `test_ticket_list.py` |

### Ticket detail & update

| Test | File |
|------|------|
| Details include comments + commenter | `test_ticket_detail_update.py` |
| 404 for missing ticket | `test_ticket_detail_update.py` |
| Valid field updates | `test_ticket_detail_update.py` |
| Status blocked on general PATCH | `test_ticket_detail_update.py` |
| Invalid assignee rejected | `test_ticket_detail_update.py` |

### State machine (integration)

| Test | File |
|------|------|
| 5 valid transitions | `test_status_transitions.py` |
| 6+ invalid transitions (incl. same-status) | `test_status_transitions.py` |
| Rejected transitions leave DB status unchanged | `test_status_transitions.py` |
| Successful transition updates `updatedAt` | `test_status_transitions.py` |
| Invalid status enum → 422 | `test_status_transitions.py` |
| Missing ticket → 404 | `test_status_transitions.py` |

### State machine (unit)

| Test | File |
|------|------|
| Allowed transition sets | `test_status_machine.py` |
| Domain validation errors | `test_status_machine.py` |

### Comments

| Test | File |
|------|------|
| Valid creation | `test_comments.py` |
| Blank message | `test_comments.py` |
| Missing ticket / invalid user | `test_comments.py` |
| Persistence + chronological order | `test_comments.py` |

### CSV export

| Test | File |
|------|------|
| Creator-scoped export | `test_export.py` |
| Comma/quote escaping | `test_export.py` |
| Empty header-only | `test_export.py` |
| Invalid user | `test_export.py` |
| Response headers | `test_export.py` |
| Formula injection (=, +, -, @) | `test_export.py` |

---

## 5. Helpers

`tests/helpers.py`:

- `acting_user_header(user_id)` — X-User-Id header dict
- `assert_error(response, status_code, code)` — error envelope assertion
- `create_ticket_via_api(...)` — POST helper
- `add_ticket_row(...)` — direct DB insert for filter tests
- `transition_status(...)` — PATCH status helper
- `reload_ticket(...)` — refresh ORM entity from DB

---

## 6. Running Tests

```bash
cd src/backend
source .venv/bin/activate
pytest ../../tests -v
```

Quick run:

```bash
pytest ../../tests -q
```

---

## 7. Recording Results

Update [test-results.md](./test-results.md) after each test run during development.

---

## 8. Frontend Tests (Separate)

Vitest + RTL in `src/frontend/` — not part of backend suite. Run with `npm test` from `src/frontend/`.
