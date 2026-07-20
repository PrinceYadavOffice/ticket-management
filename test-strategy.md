# Test Strategy

## Overview

| Layer | Framework | Location |
|-------|-----------|----------|
| Backend unit | Pytest | `tests/backend/` |
| Backend integration | Pytest + FastAPI TestClient | `tests/integration/` |
| Frontend unit/component | Vitest + React Testing Library | `src/frontend/src/**/*.test.tsx` |

---

## Backend Tests

### Unit

- Status machine: all allowed transitions succeed
- Status machine: all disallowed transitions raise/return error
- CSV builder: escaping, columns, acting-user filter
- Pydantic schema validation edge cases

### API (TestClient)

- Each endpoint: happy path + primary error paths
- `X-User-Id` missing/invalid on protected routes
- Filter/search query combinations

### Integration (Priority)

**Status transitions** — mandatory per requirements:

| Test | From | To | Expected |
|------|------|-----|----------|
| IT-S-01 | Open | In Progress | 200 |
| IT-S-02 | In Progress | Resolved | 200 |
| IT-S-03 | Resolved | Closed | 200 |
| IT-S-04 | Open | Cancelled | 200 |
| IT-S-05 | In Progress | Cancelled | 200 |
| IT-S-06 | Open | Resolved | 422 |
| IT-S-07 | Closed | Open | 422 |
| IT-S-08 | Cancelled | In Progress | 422 |
| IT-S-09 | Resolved | Open | 422 |
| IT-S-10 | Open | Closed | 422 |

Use isolated DB per test (SQLite in-memory or tempfile).

---

## Frontend Tests

### Component (RTL)

- User selector renders seeded users and updates context
- Create form shows validation errors from API
- Ticket list renders rows from mock API
- Error alert displays API message

### Not in Core

- E2E Playwright/Cypress (Stretch)

---

## Running Tests

```bash
# Backend (from repo root)
cd src/backend && pytest ../../tests -v

# Frontend
cd src/frontend && npm test
```

---

## Recording Results

Update [test-results.md](./test-results.md) after each test run during development.

---

## Coverage Goals (Core)

- Status machine service: 100% branch coverage
- Integration: all 5 valid + ≥5 invalid transitions
- Frontend: ≥1 test per major view
