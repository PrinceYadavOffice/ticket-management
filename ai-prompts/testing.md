# Testing Phase Prompts

## Purpose

Write and run tests; update test-results.md.

## Template

```
Context: Support Ticket Management System

Read: test-strategy.md, acceptance-criteria.md

Task: [TEST TASK — e.g., integration tests for status transitions]

Required integration tests (status):
- Valid: Open→In Progress, In Progress→Resolved, Resolved→Closed, Open→Cancelled, In Progress→Cancelled
- Invalid: at least 5 rejected transitions

Output: Test files under tests/ and src/frontend/src/**/*.test.tsx
Record results in test-results.md
```

## Sessions

| Date | Suite | Result |
|------|-------|--------|
| — | — | Not run (scaffold) |
