# Prompt History: Frontend Core Implementation

See [TEMPLATE.md](./TEMPLATE.md).

---

## Session Metadata

| Field | Value |
|-------|-------|
| Date | 2026-07-22 |
| Tool | Cursor |
| Phase | Implementation (M5) |
| Branch | `main` |
| Commit | `e9b5ca1` |

## Objective

Implement complete Core React frontend per `ui-flow.md` and `api-contract.md`.

## Prompt Summary

Build ticket list, create, detail pages; acting-user selector; filters; status actions; comments; CSV export; focused frontend tests; run tsc/test/build.

## AI Output Summary

- `api/client.ts`, `api/tickets.ts`, `ActingUserContext`
- Pages: `TicketListPage`, `TicketCreatePage`, `TicketDetailPage`
- Components: layout, filters, list, form, status actions, comments, export
- 20 Vitest tests, `App.css` styling

## Accepted

- `allowedStatusTransitions` from API drives status buttons
- `localStorage` for acting user
- Error/loading/empty/not-found states

## Changed

- Test assertions: `findByDisplayValue` instead of `findByText` for form fields
- `tsconfig.json` exclude `*.test.ts(x)` from production tsc

## Rejected

- Frontend `STATUS_ACTIONS` constant (backend is source of truth)
- Authentication UI

## Validation

```bash
npm test      # 20 passed
npm run build # success
```

## Follow-Up

Core quality review.
