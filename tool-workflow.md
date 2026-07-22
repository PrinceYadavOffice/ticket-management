# Tool Workflow

How Cursor and AI assistance were used to deliver this project end-to-end.

---

## Tools Used

| Tool | Role |
|------|------|
| **Cursor** | Primary IDE with Agent mode for planning, implementation, testing, review, documentation |
| **Git** | Version control; feature branch `cursor/core-quality-review-fixes` |
| **Pytest** | Backend verification gate (68 tests) |
| **Vitest + RTL** | Frontend verification gate (25 tests) |
| **FastAPI `/docs`** | Manual API exploration |
| **curl** | Live endpoint verification during review |

---

## How Cursor Was Used

1. **Agent mode** for multi-file implementation (backend services, frontend pages, tests)
2. **`.cursor/rules/`** for persistent constraints (no auth in Core, status machine on backend, `X-User-Id` semantics)
3. **`ai-prompts/`** phase templates to structure each session's goals and outputs
4. **Parallel tool calls** for reading files, running tests, and exploring codebase during review
5. **Explicit verification requests** — "run tests", "fix all errors" — to avoid unverified claims

---

## How Context Was Supplied

| Context type | Examples |
|--------------|----------|
| **Repository files** | `requirements-analysis.md`, `api-contract.md`, `implementation-plan.md` read before coding |
| **User specifications** | Full milestone prompts pasted into chat (backend Core, frontend Core, review) |
| **Prior session summaries** | Conversation summaries when context window truncated |
| **Live command output** | Test failures, curl responses, build errors fed back for fixes |
| **Cursor rules** | Always-applied workspace rules (security, minimal diffs, no commit unless asked) |

Context was **not** supplied via external tickets, Slack, or production credentials.

---

## Phase Workflows

### Requirement analysis

1. User provided full project brief (entities, state machine, acting-user, tech stack, doc list)
2. AI produced `requirements-analysis.md`, `acceptance-criteria.md`, `implementation-plan.md`
3. Human reviewed Core vs Stretch boundaries before implementation

**Prompt template:** `ai-prompts/planning.md`

### Planning

1. Scaffold repository structure per brief
2. Create planning docs, `.gitignore`, `.env.example`, Cursor rules, AI prompt templates
3. Exit: cloneable repo with no feature code

**Artifact:** `artifacts/prompt-history/2026-07-18-initial-scaffold.md`

### Design

1. Review planning docs
2. Produce `design-notes.md`, `data-model.md`, `api-contract.md`, `ui-flow.md`, `test-strategy.md`
3. Human approved API prefix `/api/`, error envelope, 409 for invalid transitions, Critical priority

**Artifact:** `artifacts/prompt-history/2026-07-20-design-complete.md`

### Code generation (implementation)

1. Read design docs + milestone section in `implementation-plan.md`
2. Implement backend (M1–M4): models, migration, services, routes, seed, tests
3. Implement frontend (M5): API client, context, pages, components, styles, tests
4. Run `pytest` / `npm test` / `npm run build` after each milestone
5. Update `ai-prompts/implementation.md` session log

**Artifacts:** `ai-prompts/implementation.md`, commits `45c0b7e`, `e9b5ca1`

### Validation

1. Run full test suites
2. Live curl matrix for error codes (401, 404, 422, 409)
3. Clean setup: remove DB → migrate → seed ×2 → tests → build
4. Record in `test-results.md`

### Testing

1. Backend: expand from 40 → 65 → 68 tests with isolated SQLite per test
2. Frontend: focused RTL tests per acceptance criteria areas
3. Reject tests that assert implementation details over behavior

**Artifact:** `ai-prompts/testing.md`

### Debugging

1. Reproduce with curl or failing test output
2. Trace to root cause (e.g., unhandled `ValidationError` on PATCH)
3. Minimal fix + regression test
4. Log in `debugging-notes.md`

**Artifact:** `ai-prompts/debugging.md`, entry 2026-07-22 PATCH 500 bug

### Code review

1. Clean setup verification + live API matrix
2. Subagent exploration of backend/frontend
3. Classify findings (Critical/High/Medium/Low/Rejected)
4. Apply accepted fixes only; reject over-engineering
5. Re-run all suites

**Artifacts:** `code-review-notes.md`, `review-fixes.md`, `ai-prompts/code-review.md`

### Documentation (submission audit)

1. Inspect actual repo — do not claim unverified results
2. Run final clean verification checklist
3. Update README, submission artifacts, compliance mapping
4. Flag remaining placeholders for candidate

**Artifact:** `compliance-checklist.md`, this file

---

## Information Intentionally Not Shared

| Not shared | Reason |
|------------|--------|
| Production credentials / API keys | None exist; Core uses local SQLite |
| Real user PII | Seed data uses `.example` emails |
| Proprietary employer code | Greenfield project |
| Exact Cursor model version per session | Not consistently logged — noted as limitation |
| Screen recordings | Not captured in repo |

---

## Quality Gates (enforced each session)

- [x] `pytest tests` passes
- [x] `npm test` passes
- [x] `npm run build` passes (frontend)
- [x] Planning/design docs updated when behavior changed
- [x] Prompt history or `ai-prompts/*.md` session log updated
- [x] No secrets or generated artifacts committed

---

## Reusing This Workflow

1. **Start with planning docs** — requirements, acceptance criteria, implementation plan before code
2. **Lock API contract** — design phase before M1; treat contract as source of truth
3. **Use milestone prompts** — copy `ai-prompts/<phase>.md` template into Cursor with specific task
4. **Verify every claim** — run tests and curl; paste output into chat on failure
5. **Keep Cursor rules** — encode non-negotiables (no auth, state machine location)
6. **Log sessions** — `artifacts/prompt-history/TEMPLATE.md` per significant interaction
7. **Review before submit** — compliance checklist + clean DB verification
8. **Reject scope creep** — document Stretch items as not implemented

---

## Cursor-Specific Reference

See [tool-specific/cursor-workflow/README.md](./tool-specific/cursor-workflow/README.md) for branch naming and agent instructions.

## Prompt History Index

| Date | File | Phase |
|------|------|-------|
| 2026-07-18 | `artifacts/prompt-history/2026-07-18-initial-scaffold.md` | Planning |
| 2026-07-20 | `artifacts/prompt-history/2026-07-20-design-complete.md` | Design |
| 2026-07-20 | `artifacts/prompt-history/2026-07-20-backend-core.md` | Implementation |
| 2026-07-20 | `artifacts/prompt-history/2026-07-20-backend-tests.md` | Testing |
| 2026-07-22 | `artifacts/prompt-history/2026-07-22-frontend-core.md` | Implementation |
| 2026-07-22 | `artifacts/prompt-history/2026-07-22-quality-review.md` | Code review |
| 2026-07-22 | `artifacts/prompt-history/2026-07-22-submission-audit.md` | Documentation |
