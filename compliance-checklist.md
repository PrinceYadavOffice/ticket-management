# Compliance Checklist

**Audit date:** 2026-07-22  
**Branch:** `cursor/core-quality-review-fixes`  
**Verifier:** Clean local run (DB removed → migrate → seed ×2 → tests → build → API curls)

---

## Verification Run (2026-07-22)

| Step | Command / action | Result |
|------|------------------|--------|
| 1 | `rm data/tickets.db` | Pass |
| 2 | `pip install -r requirements.txt` | Pass |
| 3 | `npm ci` (frontend) | Pass |
| 4 | `alembic upgrade head` | Pass |
| 5 | `python -m app.scripts.seed` ×2 | Pass — 4 users, 6 tickets, 6 comments (idempotent) |
| 6 | `pytest tests -q` | **68 passed** |
| 7 | `npm test` | **25 passed** |
| 8 | `npm run build` | Pass |
| 9 | `uvicorn` + endpoint curls | health/users/tickets/export → 200 |
| 10 | `git ls-files` secrets check | No `.env`, `data/`, `node_modules`, `dist/` tracked |

---

## Core Requirement Mapping

### Acting-user context

| Req | Implementation | Test | Documentation | Status |
|-----|----------------|------|---------------|--------|
| AC-01 User selector | `ActingUserSelector.tsx`, `ActingUserContext.tsx` | `App.test.tsx` | README, api-contract §1 | **Pass** |
| AC-02 X-User-Id header | `api/client.ts` | `api/tickets.test.ts` | design-notes, README | **Pass** |
| AC-03 Not auth disclaimer | `AppLayout.tsx` | `App.test.tsx` | README, api-contract | **Pass** |
| AC-04 Missing header | `dependencies.py` | `test_ticket_create.py` | api-contract | **Pass** |
| AC-05 Invalid header | `dependencies.py` | `test_ticket_create.py` | api-contract | **Pass** |

### Tickets — create & list

| Req | Implementation | Test | Documentation | Status |
|-----|----------------|------|---------------|--------|
| AC-10 Create Open ticket | `ticket_service.create_ticket` | `test_ticket_create.py` | api-contract | **Pass** |
| AC-11 createdBy from header | `ticket_service.py` | `test_ticket_create.py` | data-model | **Pass** |
| AC-12 Timestamps | models + service | `test_ticket_create.py` | data-model | **Pass** |
| AC-13 List tickets | `ticket_service.list_tickets` | `test_ticket_list.py`, `TicketList.test.tsx` | api-contract | **Pass** |
| AC-14 Required field 422 | Pydantic schemas | `test_ticket_create.py` | api-contract | **Pass** |
| AC-15 Frontend validation errors | `TicketForm.tsx`, `ErrorAlert.tsx` | `TicketForm.test.tsx` | ui-flow | **Pass** |

### Tickets — detail & update

| Req | Implementation | Test | Documentation | Status |
|-----|----------------|------|---------------|--------|
| AC-20 Detail + comments | `get_ticket_detail` | `test_ticket_detail_update.py` | api-contract | **Pass** |
| AC-21 404 missing ticket | `ticket_service` | `test_ticket_detail_update.py` | api-contract | **Pass** |
| AC-22 PATCH fields | `update_ticket` | `test_ticket_detail_update.py` | api-contract | **Pass** |
| AC-23 updatedAt changes | service | `test_ticket_detail_update.py` | data-model | **Pass** |
| AC-24 Invalid assignee | service validation | `test_ticket_detail_update.py` | api-contract | **Pass** |
| AC-25 Detail view fields | `TicketDetailPage.tsx` | `TicketDetailPage.test.tsx` | ui-flow | **Pass** |

### Comments

| Req | Implementation | Test | Documentation | Status |
|-----|----------------|------|---------------|--------|
| AC-30 Add comment | `comment_service.py` | `test_comments.py` | api-contract | **Pass** |
| AC-31 createdBy/createdAt | model + service | `test_comments.py` | data-model | **Pass** |
| AC-32 Comments on detail | `CommentList.tsx` | `TicketDetailPage.test.tsx` | ui-flow | **Pass** |
| AC-33 404 on missing ticket | `comment_service` | `test_comments.py` | api-contract | **Pass** |
| AC-34 Empty message rejected | `CommentCreate` schema | `test_comments.py`, `CommentForm.test.tsx` | api-contract | **Pass** |

### Status state machine

| Req | Implementation | Test | Documentation | Status |
|-----|----------------|------|---------------|--------|
| AC-40–44 Valid transitions | `status_machine.py` | `test_status_transitions.py` | README, design-notes | **Pass** |
| AC-45–47 Invalid transitions | `status_machine.py` | `test_status_transitions.py` | api-contract | **Pass** |
| AC-48 Error shape 409 | `exceptions.py` | `test_status_transitions.py` | api-contract | **Pass** |
| AC-49 UI reflects status | `TicketStatusActions.tsx` | `TicketStatusActions.test.tsx` | ui-flow | **Pass** |

### Search & filter

| Req | Implementation | Test | Documentation | Status |
|-----|----------------|------|---------------|--------|
| AC-50 Filter status | `ticket_service.list_tickets` | `test_ticket_list.py` | api-contract | **Pass** |
| AC-51 Filter priority | same | `test_ticket_list.py` | api-contract | **Pass** |
| AC-52 Keyword search | same | `test_ticket_list.py` | api-contract | **Pass** |
| AC-53 Frontend filter UI | `TicketFilters.tsx`, `TicketListPage.tsx` | `TicketFilters.test.tsx` | ui-flow | **Pass** |
| AC-54 Empty results 200 | list service | `test_ticket_list.py` | api-contract | **Pass** |

### CSV export

| Req | Implementation | Test | Documentation | Status |
|-----|----------------|------|---------------|--------|
| AC-60 text/csv | `csv_export.py` | `test_export.py` | api-contract | **Pass** |
| AC-61 createdBy scope | `csv_export.build_tickets_csv` | `test_export.py` | README | **Pass** |
| AC-62 Header row | `csv_export.py` | `test_export.py` | api-contract | **Pass** |
| AC-63 Frontend download | `TicketExportButton.tsx` | — | ui-flow | **Pass** (manual; no automated export test) |
| AC-64 Headers-only empty | `csv_export.py` | `test_export.py` | api-contract | **Pass** |

### Persistence

| Req | Implementation | Test | Documentation | Status |
|-----|----------------|------|---------------|--------|
| AC-70 Tickets survive restart | SQLite file | Manual curl after restart | README troubleshooting | **Pass** |
| AC-71 Comments survive restart | SQLite file | Manual / integration | data-model | **Pass** |
| AC-72 Migrations on fresh DB | `001_initial.py` | Clean audit run | database/setup-notes | **Pass** |

### Frontend quality

| Req | Implementation | Test | Documentation | Status |
|-----|----------------|------|---------------|--------|
| AC-80 Loading states | `LoadingSpinner`, disabled buttons | Manual | ui-flow §9 | **Pass** |
| AC-81 API errors displayed | `ErrorAlert.tsx` | `ErrorAlert.test.tsx` | ui-flow | **Pass** |
| AC-82 Build clean | `tsconfig.json`, Vite | `npm run build` | test-results | **Pass** |
| AC-83 No console errors | — | Manual recommended | — | **Not automated** |

### Test coverage minimum

| Req | Implementation | Test | Documentation | Status |
|-----|----------------|------|---------------|--------|
| AC-90 Pytest passes | `tests/` | 68 passed | test-results | **Pass** |
| AC-91 Valid transitions tested | `test_status_transitions.py` | 15 tests | test-strategy | **Pass** |
| AC-92 Invalid transitions tested | same | included | test-strategy | **Pass** |
| AC-93 Vitest passes | `src/frontend/src/**/*.test.*` | 25 passed | test-results | **Pass** |
| AC-94 RTL per major view | list/detail/create | See note below | test-strategy | **Partial** |

**AC-94 gap:** No `TicketCreatePage.test.tsx`. Create flow covered by `TicketForm.test.tsx` (component-level). List covered by `TicketList.test.tsx` (component) not `TicketListPage.test.tsx`.

---

## Submission Artifacts

| Artifact | File | Status |
|----------|------|--------|
| README | `README.md` | **Complete** |
| Candidate info | `candidate-info.md` | **Placeholders** — candidate must fill |
| Tool workflow | `tool-workflow.md` | **Complete** |
| Requirements | `requirements-analysis.md` | **Complete** (v1.0 content; status updated) |
| Acceptance criteria | `acceptance-criteria.md` | **Complete** |
| Implementation plan | `implementation-plan.md` | **Complete** (milestones marked done) |
| Design notes | `design-notes.md` | **Complete** |
| API contract | `api-contract.md` | **Complete** |
| Data model | `data-model.md` | **Complete** |
| UI flow | `ui-flow.md` | **Complete** |
| Test strategy | `test-strategy.md` | **Updated** |
| Test results | `test-results.md` | **Complete** |
| Debugging notes | `debugging-notes.md` | **Complete** |
| Code review | `code-review-notes.md` | **Complete** |
| Review fixes | `review-fixes.md` | **Complete** |
| PR description | `pr-description.md` | **Complete** |
| Reflection | `reflection.md` | **Complete** |
| AI usage summary | `final-ai-usage-summary.md` | **Complete** |
| Prompt history | `artifacts/prompt-history/` | **6 sessions** |
| Compliance checklist | `compliance-checklist.md` | **This file** |

---

## Items Still Incomplete (candidate action)

1. **`candidate-info.md`** — personal details, hours, self-assessment placeholders
2. **Screenshots / demo** — placeholders in `pr-description.md`; no images in repo
3. **AC-94** — optional: add `TicketCreatePage.test.tsx` for full page-level coverage
4. **AC-83** — manual smoke test of browser console not recorded in CI
5. **PR merge** — feature branch pushed; `gh` not authenticated to open PR automatically
6. **Prompt history** — some entries retain `[MODEL_NAME]` / `[MINUTES]` placeholders
