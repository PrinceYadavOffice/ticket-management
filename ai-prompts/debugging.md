# Debugging Phase Prompts

## Purpose

Diagnose failures; document in `debugging-notes.md`.

---

## Session: 2026-07-20 — Test Suite Verification

### Context

After expanding backend tests to 65 cases covering all Core API requirements.

### Process

1. Ran full suite: `pytest ../../tests -v` from `src/backend/`
2. Reviewed failures (none)
3. Verified separate test DB via `tmp_path` fixture — production `data/tickets.db` untouched

### Outcome

No debugging required. All tests passed on first run after fixing:
- Syntax error in `test_status_transitions.py` (`else` indentation) during test authoring
- Removed duplicate `sample_ticket` fixture definition

### Notes for Future Debugging

| Symptom | Likely cause | Check |
|---------|--------------|-------|
| `ModuleNotFoundError: app` | PYTHONPATH | `tests/conftest.py` path insert |
| Pydantic validation on TicketResponse | ORM alias mismatch | `validation_alias` in schemas |
| 409 vs 422 on status | Wrong HTTP code in service | `status_machine.py` uses 409 |
| CSV formula test fails | Missing sanitize prefix | `csv_export._sanitize_csv_cell` |

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
| 2026-07-20 | Test expansion | No implementation bugs found |
| 2026-07-20 (earlier) | Pydantic ORM mapping | `validation_alias` on ticket schemas |
