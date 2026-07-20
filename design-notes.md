# Design Notes

## Acting-User Context (Not Authentication)

### Decision

The application simulates "who is performing this action" without implementing real authentication.

### Mechanism

1. Users are **seeded** in the database at startup/migration.
2. The frontend renders a **current user selector** populated from `GET /users`.
3. Every API request includes header: `X-User-Id: <integer>`.
4. Backend resolves the header to a User record; rejects missing/invalid IDs.

### What This Is

- Acting-user context for `createdBy`, comment authorship, and CSV export scope
- A development/demo convenience

### What This Is Not

- Authentication (no passwords, tokens, or sessions)
- Authorization (Core does not enforce roles; any seeded user can act)

### Security Implications

Do not deploy this pattern to production without replacing it with proper auth. Document prominently in README and API contract.

### Frontend UX

- Persistent banner or label: "Acting as: [Name] (demo mode — not authenticated)"
- Selector change should refresh lists where user-scoped data applies

---

## Status State Machine

Centralize transition rules in `src/backend/app/services/status_machine.py` (planned).

```
Open ──────────► In Progress ──► Resolved ──► Closed
  │                    │
  └──── Cancelled ◄────┘
```

Invalid transitions return HTTP 422 with error code `invalid_status_transition`.

---

## Error Response Shape (Planned)

```json
{
  "detail": "Human-readable message",
  "code": "invalid_status_transition",
  "fields": { "status": "Cannot transition from Closed to Open" }
}
```

---

## Open Design Questions

See [requirements-analysis.md](./requirements-analysis.md) § Product Owner Clarification Questions.
