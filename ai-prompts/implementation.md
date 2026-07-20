# Implementation Phase Prompts

## Purpose

Guide milestone-based feature implementation.

## Template

```
Context: Support Ticket Management System — Milestone [MX]

Read first:
- implementation-plan.md (milestone section)
- api-contract.md
- data-model.md
- .cursor/rules/

Task: [IMPLEMENTATION TASK]

Constraints:
- Match existing code patterns in src/backend and src/frontend
- Backend validation required; meaningful frontend errors
- No authentication in Core
- Run tests after changes

Output: Code + update relevant docs if contract changed.
```

## Sessions

| Date | Milestone | Summary |
|------|-----------|---------|
| — | — | Scaffold only (M0 complete) |
