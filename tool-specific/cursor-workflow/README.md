# Cursor Workflow

Project-specific guidance for using Cursor on this repository.

## Rules Location

`.cursor/rules/` — always-applied and file-specific rules including:

- No authentication in Core unless explicitly requested
- Status machine enforced on backend only
- Minimal, reviewable diffs
- Run tests after behavior changes
- Do not commit secrets

## Recommended Workflow

1. Open **repository root** in Cursor
2. Read `implementation-plan.md` for current milestone
3. Copy phase prompt from `ai-prompts/<phase>.md` into Agent chat
4. Attach or reference: `api-contract.md`, `acceptance-criteria.md`, relevant design docs
5. After session: log in `artifacts/prompt-history/`, update `ai-prompts/<phase>.md`
6. Run tests before ending session

## Branch Naming

```
cursor/<milestone-or-topic>-<short-summary>
```

Examples:
- `cursor/m1-data-layer`
- `cursor/core-quality-review-fixes`

**Note:** `main` may be protected — use feature branches + PR.

## Agent Instructions

- Read `requirements-analysis.md` and `api-contract.md` before API changes
- Never implement authentication unless explicitly requested (Stretch)
- Status transitions must be enforced in `status_machine.py` only
- Frontend uses `allowedStatusTransitions` from API — do not duplicate rules in UI constants
- Send `X-User-Id` from `api/client.ts` for protected routes (create, comment, export)
- Update planning docs when behavior changes
- Verify claims with `pytest`, `npm test`, `npm run build` — paste output on failure

## Context Supply Tips

| Do | Don't |
|----|-------|
| Paste milestone requirements verbatim | Assume AI remembers prior sessions |
| Reference file paths (`api-contract.md §4`) | Vague "implement tickets" |
| Share test failure output | Claim "tests pass" without running |
| State Core vs Stretch boundaries | Let AI add auth/CI unprompted |

## Useful Commands

```bash
# Backend
cd src/backend && source .venv/bin/activate
alembic upgrade head
python -m app.scripts.seed
uvicorn app.main:app --reload --port 8000

# Frontend
cd src/frontend && npm run dev

# Tests (from repo root)
cd src/backend && source .venv/bin/activate && pytest ../../tests -v
cd src/frontend && npm test && npm run build

# Clean verification
rm -f data/tickets.db && alembic upgrade head && python -m app.scripts.seed
```

## Submission Checklist

See [compliance-checklist.md](../compliance-checklist.md) and [candidate-info.md](../candidate-info.md).

## Prompt History

Log significant sessions using [artifacts/prompt-history/TEMPLATE.md](../artifacts/prompt-history/TEMPLATE.md).
