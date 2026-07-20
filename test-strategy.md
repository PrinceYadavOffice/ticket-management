# Test Strategy

**Version:** 1.0  
**Last Updated:** 2026-07-20  
**Status:** Design complete — ready for implementation alongside features

---

## 1. Goals

- Verify all Core acceptance criteria ([acceptance-criteria.md](./acceptance-criteria.md))
- Catch status machine regressions with dedicated unit and integration tests
- Ensure consistent error envelope across endpoints
- Keep tests fast and isolated (in-memory SQLite per test session)

---

## 2. Test Pyramid

```
                    ┌─────────────┐
                    │   Manual    │  persistence restart, CSV download
                    ├─────────────┤
                    │  Component  │  Vitest + RTL (frontend)
                    ├─────────────┤
                    │ Integration │  status transitions E2E via API
                    ├─────────────┤
                    │  API tests  │  each endpoint + errors
                    ├─────────────┤
                    │    Unit     │  status_machine, csv_export
                    └─────────────┘
```

---

## 3. Test Infrastructure

### Backend

| Item | Approach |
|------|----------|
| Framework | Pytest |
| HTTP client | FastAPI `TestClient` |
| Database | SQLite `:memory:` or temp file per test function |
| Fixtures | `tests/conftest.py`: `db`, `client`, `seeded_users`, `sample_ticket` |
| Migrations | Create tables via metadata or run Alembic once per session |

```python
# conftest pattern (planned)
@pytest.fixture
def client(db_session, seeded_users):
    app.dependency_overrides[get_db] = lambda: db_session
    yield TestClient(app)
    app.dependency_overrides.clear()
```

### Frontend

| Item | Approach |
|------|----------|
| Framework | Vitest |
| DOM | jsdom |
| Components | React Testing Library |
| API | Mock `fetch` or inject mock API client |
| Setup | `src/frontend/src/test/setup.ts` (`@testing-library/jest-dom`) |

---

## 4. Test Layers

### Layer 1: Domain Unit Tests (`tests/backend/`)

Pure logic — no HTTP, no database where possible.

#### `test_status_machine.py`

| ID | Test | Input | Expected |
|----|------|-------|----------|
| SM-01 | Allowed from Open | `Open` | `["In Progress", "Cancelled"]` |
| SM-02 | Allowed from In Progress | `In Progress` | `["Resolved", "Cancelled"]` |
| SM-03 | Allowed from Resolved | `Resolved` | `["Closed"]` |
| SM-04 | Terminal Closed | `Closed` | `[]` |
| SM-05 | Terminal Cancelled | `Cancelled` | `[]` |
| SM-06 | Valid transition | `Open` → `In Progress` | No exception |
| SM-07 | Invalid transition | `Open` → `Resolved` | Raises `AppError` / `INVALID_STATUS_TRANSITION` |
| SM-08 | Invalid transition | `Closed` → `Open` | Raises |
| SM-09 | Same status | `Open` → `Open` | Raises (no-op not allowed) |

**Coverage target:** 100% branch coverage on `status_machine.py`.

#### `test_csv_export.py`

| ID | Test | Expected |
|----|------|----------|
| CSV-01 | Filters by creator | Only acting user's tickets |
| CSV-02 | Header row present | Column names match contract |
| CSV-03 | Empty result | Headers only |
| CSV-04 | Comma in title | Field quoted per RFC 4180 |
| CSV-05 | Null assignee | Empty string in CSV cell |

---

### Layer 2: API Tests (`tests/backend/`)

One file per resource area. Assert HTTP status, response body shape, and error envelope.

#### `test_health.py` ✓ (exists)

| ID | Test | Expected |
|----|------|----------|
| HL-01 | GET /health | 200, `{ status: "ok" }` |

#### `test_users.py`

| ID | Test | Expected |
|----|------|----------|
| US-01 | GET /users | 200, non-empty array |
| US-02 | User shape | id, name, email, role present |

#### `test_tickets_read.py`

| ID | Test | Expected |
|----|------|----------|
| TR-01 | GET /tickets without header | 401 `MISSING_ACTING_USER` |
| TR-02 | GET /tickets with valid header | 200, array |
| TR-03 | Filter by status | Only matching tickets |
| TR-04 | Filter by priority | Only matching tickets |
| TR-05 | Filter by assignedTo | Only matching tickets |
| TR-06 | unassigned=true | Only null assignee |
| TR-07 | Search q in title | Match found |
| TR-08 | Search q in description | Match found |
| TR-09 | Combined filters AND | Intersection |
| TR-10 | No matches | 200, `[]` |
| TR-11 | GET /tickets/{id} | 200, includes comments |
| TR-12 | GET /tickets/{id} missing | 404 `NOT_FOUND` |
| TR-13 | Detail includes allowedStatusTransitions | Array present |

#### `test_tickets_write.py`

| ID | Test | Expected |
|----|------|----------|
| TW-01 | POST /tickets valid | 201, status Open, createdBy = header |
| TW-02 | POST missing title | 422 `VALIDATION_ERROR` |
| TW-03 | POST invalid priority | 422 |
| TW-04 | POST invalid assignee | 422 |
| TW-05 | POST with status field | 422 (rejected) |
| TW-06 | PATCH update title | 200, updatedAt changes |
| TW-07 | PATCH with status field | 422 (rejected) |
| TW-08 | PATCH empty body | 422 |
| TW-09 | PATCH invalid assignee | 422 |
| TW-10 | PATCH not found | 404 |

#### `test_comments.py`

| ID | Test | Expected |
|----|------|----------|
| CM-01 | POST comment valid | 201, createdBy = header |
| CM-02 | POST empty message | 422 |
| CM-03 | POST on missing ticket | 404 |

#### `test_export.py`

| ID | Test | Expected |
|----|------|----------|
| EX-01 | GET /tickets/export | 200, text/csv |
| EX-02 | Only creator's tickets | Excludes other users' tickets |
| EX-03 | No tickets | Header row only |
| EX-04 | Content-Disposition header | attachment filename present |

#### `test_acting_user.py`

| ID | Test | Expected |
|----|------|----------|
| AU-01 | Missing header on protected route | 401 `MISSING_ACTING_USER` |
| AU-02 | Non-integer header | 401 `INVALID_ACTING_USER` |
| AU-03 | Unknown user ID | 401 `ACTING_USER_NOT_FOUND` |
| AU-04 | Error envelope shape | `{ error: { code, message, details } }` |

---

### Layer 3: Integration Tests (`tests/integration/`)

Full request cycle through API + database. **Mandatory** for status transitions.

#### `test_status_transitions.py`

| ID | From | To | Expected HTTP | Error code (if fail) |
|----|------|-----|---------------|----------------------|
| IT-S-01 | Open | In Progress | 200 | — |
| IT-S-02 | In Progress | Resolved | 200 | — |
| IT-S-03 | Resolved | Closed | 200 | — |
| IT-S-04 | Open | Cancelled | 200 | — |
| IT-S-05 | In Progress | Cancelled | 200 | — |
| IT-S-06 | Open | Resolved | 422 | `INVALID_STATUS_TRANSITION` |
| IT-S-07 | Open | Closed | 422 | `INVALID_STATUS_TRANSITION` |
| IT-S-08 | Closed | Open | 422 | `INVALID_STATUS_TRANSITION` |
| IT-S-09 | Cancelled | In Progress | 422 | `INVALID_STATUS_TRANSITION` |
| IT-S-10 | Resolved | Open | 422 | `INVALID_STATUS_TRANSITION` |
| IT-S-11 | Resolved | Cancelled | 422 | `INVALID_STATUS_TRANSITION` |
| IT-S-12 | Error envelope on invalid | — | `error.code` present | |

Each test: create ticket → apply transitions in sequence → assert final state.

#### `test_persistence.py` (optional manual-assisted)

| ID | Test | Expected |
|----|------|----------|
| IT-P-01 | Create ticket, new session | Ticket retrievable |

---

### Layer 4: Frontend Component Tests (`src/frontend/src/`)

| File | Tests |
|------|-------|
| `App.test.tsx` ✓ | Title, disclaimer render |
| `ActingUserSelector.test.tsx` | Renders users; calls onChange |
| `TicketList.test.tsx` | Renders rows from mock data |
| `TicketForm.test.tsx` | Shows field errors from ApiError |
| `TicketStatusActions.test.tsx` | Renders buttons from allowedTransitions |
| `ErrorAlert.test.tsx` | Displays message and field details |

**Minimum for Core (AC-94):** one test file each for list, detail (form), create (form).

---

### Layer 5: Manual Test Checklist

| # | Scenario | Pass |
|---|----------|------|
| M-01 | Create ticket → appears in list | ☐ |
| M-02 | Filter by status | ☐ |
| M-03 | Update ticket fields | ☐ |
| M-04 | Valid status transition via UI | ☐ |
| M-05 | Invalid transition shows error | ☐ |
| M-06 | Add comment appears on detail | ☐ |
| M-07 | Export CSV downloads correct file | ☐ |
| M-08 | Restart backend — data persists | ☐ |
| M-09 | Change acting user — export scope changes | ☐ |

---

## 5. Error Envelope Assertions

Helper for API tests:

```python
def assert_error(response, status_code, code):
    assert response.status_code == status_code
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == code
    assert "message" in body["error"]
    assert "details" in body["error"]
```

Every error test should use this helper for consistency.

---

## 6. Test Data Fixtures

| Fixture | Contents |
|---------|----------|
| `user_alice` | id=1, Agent |
| `user_bob` | id=2, Admin |
| `user_carol` | id=3, Agent |
| `ticket_open` | Created by Alice, status Open |
| `ticket_in_progress` | Status In Progress |

Seed fixtures in conftest match `database/seed-data/users.json`.

---

## 7. Running Tests

```bash
# All backend tests
cd src/backend && pytest ../../tests -v

# Unit only
pytest ../../tests/backend -v

# Integration only
pytest ../../tests/integration -v

# Frontend
cd src/frontend && npm test

# With coverage (Stretch)
pytest ../../tests --cov=app --cov-report=term-missing
```

---

## 8. CI Gate (Stretch)

When CI is added:

1. `pytest` — must pass
2. `npm test` — must pass
3. `npm run build` — must pass

---

## 9. Recording Results

Update [test-results.md](./test-results.md) after each milestone with:

- Date, branch, pass/fail counts
- Any skipped or known failures

---

## 10. Traceability

| Acceptance Criteria | Test IDs |
|---------------------|----------|
| AC-04, AC-05 | AU-01–04 |
| AC-10–15 | TW-01–05, TR-01 |
| AC-20–25 | TR-11–12, TW-06 |
| AC-30–34 | CM-01–03 |
| AC-40–48 | IT-S-01–12, SM-01–09 |
| AC-50–54 | TR-03–10 |
| AC-60–64 | EX-01–04 |
| AC-90–94 | Full suite |

---

## 11. Implementation Status

| Suite | Status |
|-------|--------|
| `test_health.py` | Scaffold (1 test) |
| `test_status_transitions.py` | Placeholder only |
| All other files | Not created (implement with M2–M5) |
