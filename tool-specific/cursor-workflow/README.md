# Cursor Workflow

Project-specific guidance for using Cursor on this repository.

## Rules Location

`.cursor/rules/` — always-applied and file-specific rules.

## Recommended Workflow

1. Open repo root in Cursor
2. Start from `implementation-plan.md` milestone
3. Use phase prompts in `ai-prompts/`
4. Log session in `artifacts/prompt-history/`
5. Run tests before ending session

## Branch Naming

```
cursor/<ticket-or-milestone>-<short-summary>
```

Example: `cursor/m1-data-layer`

## Agent Instructions

- Read `requirements-analysis.md` and `api-contract.md` before API changes
- Never implement authentication unless explicitly requested (Stretch)
- Status transitions must be enforced in backend only
- Send `X-User-Id` from frontend API client for all protected routes
- Update planning docs when behavior changes

## Useful Commands

```bash
# Backend
cd src/backend && source .venv/bin/activate && uvicorn app.main:app --reload

# Frontend
cd src/frontend && npm run dev

# Tests
cd src/backend && pytest ../../tests -v
cd src/frontend && npm test
```
