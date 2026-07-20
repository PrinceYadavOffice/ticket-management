# Code Review Notes

Self-review and external review findings.

## Review Checklist

- [ ] Status machine logic only in backend service
- [ ] `X-User-Id` validated on all protected routes
- [ ] No secrets in code or commits
- [ ] API responses match `api-contract.md`
- [ ] Error shapes consistent
- [ ] Tests cover invalid status transitions
- [ ] Frontend documents acting-user disclaimer
- [ ] CSV export scoped to `createdBy` = acting user

---

## Findings

| ID | Severity | File | Finding | Status |
|----|----------|------|---------|--------|
| — | — | — | No code reviewed yet (scaffold phase) | — |
