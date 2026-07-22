# Debugging Phase Prompts

## Purpose

Diagnose failures; document in `debugging-notes.md`.

---

## Session: 2026-07-22 — Core Quality Review

### Context

Full-stack review: clean setup verification, live API matrix, senior code review, apply accepted fixes.

### Process

1. `pip install`, `npm ci`, `alembic upgrade head`, seed ×2
2. Started backend; ran curl matrix for all validation scenarios
3. Found `PATCH /api/tickets/{id}` returning 500 for validation failures
4. Fixed exception handlers + frontend error-handling issues
5. Added regression tests; re-ran `pytest` (68) and `npm test` (25)

### Bugs Found (real)

| Bug | Root cause | Fix |
|-----|------------|-----|
| PATCH validation → 500 | Unhandled `ValidationError` / `JSONDecodeError` | Global handlers in `exceptions.py` |
| Comment text lost | Sync clear before async submit | `await onSubmit` in `CommentForm` |

### Outcome

All test suites and production build pass after fixes. See `debugging-notes.md` and `review-fixes.md`.

### Notes for Future Debugging

| Symptom | Likely cause | Check |
|---------|--------------|-------|
| PATCH ticket returns 500 on bad input | Manual `model_validate` without handler | `exceptions.py` ValidationError handler |
| Comment disappears on error | Form clears before await | `CommentForm.handleSubmit` |
| Acting user resets | Fetch overwrites selection | `ActingUserContext` setState callback |
| `ModuleNotFoundError: app` | PYTHONPATH | `tests/conftest.py` |
| 409 vs 422 on status | Wrong HTTP code | `status_machine.py` uses 409 |
| localhost not working | Servers not running | Start backend :8000 + frontend :5173 |

---

## Session: 2026-07-20 — Test Suite Verification

### Context

After expanding backend tests to 65 cases covering all Core API requirements.

### Outcome

No implementation bugs found at that time. PATCH validation gap discovered in 2026-07-22 review.

---

## Template

```
Context: Support Ticket Management System

Symptom: [ERROR OR UNEXPECTED BEHAVIOR]

Environment:
- Branch: [BRANCH]
- Commands run: [COMMANDS]

Relevant files: [PATHS]

Task: Root cause analysis and minimal fix.

Output: Fix + entry in debugging-notes.md
```

## Sessions

| Date | Issue | Resolution |
|------|-------|------------|
| 2026-07-22 | PATCH validation 500 | Exception handlers + 3 regression tests |
| 2026-07-22 | Comment form clear race | await onSubmit + rethrow |
| 2026-07-20 | Test expansion | No bugs at that time |
| 2026-07-20 (earlier) | Pydantic ORM mapping | `validation_alias` on ticket schemas |
