# Code Review Phase Prompts

## Purpose

Structured self-review before PR.

## Template

```
Context: Support Ticket Management System

Diff: [branch changes | uncommitted changes]

Review against:
- acceptance-criteria.md (Core items)
- api-contract.md
- design-notes.md (X-User-Id, state machine)
- Security: no secrets, input validation

Output: Findings in code-review-notes.md; fixes in review-fixes.md
```

---

## Session: 2026-07-22 — Core Quality Review (Full Stack)

### Scope

Backend + frontend Core implementation. No Stretch features.

### Process

1. Clean setup verification (install, migrate, seed, startup, CORS, live API)
2. Validation/error matrix (curl + existing tests)
3. Senior review: maintainability, state machine, transactions, CSV safety, a11y, tests
4. Classified 20 findings (Critical: 0; High: 3; Medium: 6; Low: 7; Rejected: 4)
5. Applied 13 accepted fixes; rejected unnecessary refactors and Stretch suggestions
6. Re-ran all suites: 68 backend, 25 frontend, production build OK

### Key finding

**CR-01 (High):** `PATCH /api/tickets/{id}` returned HTTP 500 for validation errors — fixed with Pydantic/JSON exception handlers.

### Documents updated

- `code-review-notes.md`
- `review-fixes.md`
- `debugging-notes.md`
- `test-results.md`
- `ai-prompts/debugging.md`
- `ai-prompts/code-review.md` (this file)

---

## Sessions

| Date | Scope | Findings | Fixes applied |
|------|-------|----------|---------------|
| 2026-07-22 | Full stack Core | 20 classified (3 High bugs) | 13 changed, 7 rejected |
