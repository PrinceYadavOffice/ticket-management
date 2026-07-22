# Requirements Analysis

## Support Ticket Management System

**Version:** 1.0  
**Last Updated:** 2026-07-22  
**Status:** Implemented — all Core functional requirements delivered

---

## 1. Overview

Build a full-stack support ticket management application that allows users to create, view, update, and comment on tickets. Data persists in SQLite across restarts. The system enforces a strict ticket status state machine on the backend. Authentication is **not** part of Core; acting-user context is simulated via a seeded user selector and `X-User-Id` header.

---

## 2. Functional Requirements

### 2.1 User Management (Seeded Only)

| ID | Requirement |
|----|-------------|
| FR-U-01 | The system shall store users with: `id`, `name`, `email`, `role`. |
| FR-U-02 | Users shall be seeded at database initialization; no user CRUD in Core. |
| FR-U-03 | The frontend shall provide a selector to choose the current acting user from seeded users. |
| FR-U-04 | The selected user ID shall be sent on API requests via the `X-User-Id` header. |

### 2.2 Ticket Management

| ID | Requirement |
|----|-------------|
| FR-T-01 | Users shall create tickets with `title`, `description`, and `priority`. |
| FR-T-02 | New tickets shall default to status `Open`. |
| FR-T-03 | `createdBy` shall be set from the acting user (`X-User-Id`). |
| FR-T-04 | Users shall list tickets with optional search/filter. |
| FR-T-05 | Users shall view ticket details including comments. |
| FR-T-06 | Users shall update `title`, `description`, `priority`, and `assignedTo`. |
| FR-T-07 | `updatedAt` shall be set automatically on ticket modifications. |
| FR-T-08 | Users shall export all tickets **created by the current acting user** as CSV. |

### 2.3 Comments

| ID | Requirement |
|----|-------------|
| FR-C-01 | Users shall add comments to tickets with a `message`. |
| FR-C-02 | `createdBy` and `createdAt` shall be set automatically. |
| FR-C-03 | Comments shall be associated with a ticket via `ticketId`. |

### 2.4 Status State Machine

| ID | Requirement |
|----|-------------|
| FR-S-01 | Allowed statuses: `Open`, `In Progress`, `Resolved`, `Closed`, `Cancelled`. |
| FR-S-02 | Allowed transitions (backend-enforced): |

| From | To |
|------|-----|
| Open | In Progress |
| Open | Cancelled |
| In Progress | Resolved |
| In Progress | Cancelled |
| Resolved | Closed |

| ID | Requirement |
|----|-------------|
| FR-S-03 | All other status transitions shall be rejected by the backend with a meaningful error. |
| FR-S-04 | Status changes shall update `updatedAt`. |

### 2.5 Search and Filter

| ID | Requirement |
|----|-------------|
| FR-F-01 | Users shall search or filter tickets (e.g., by status, priority, title keyword, assignee). |
| FR-F-02 | Filter criteria may be combined (AND logic) unless otherwise specified in API contract. |

### 2.6 Validation and Errors

| ID | Requirement |
|----|-------------|
| FR-V-01 | Backend shall validate all inputs (required fields, enums, foreign keys, state machine). |
| FR-V-02 | Frontend shall display meaningful error messages from API responses. |
| FR-V-03 | Missing or invalid `X-User-Id` shall return an appropriate HTTP error. |

### 2.7 Data Persistence

| ID | Requirement |
|----|-------------|
| FR-D-01 | All entities shall persist in SQLite. |
| FR-D-02 | Data shall survive application restart. |
| FR-D-03 | Schema changes shall be managed via Alembic migrations. |

---

## 3. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-01 | Maintainability | Code organized into backend (`src/backend`) and frontend (`src/frontend`) with clear separation of concerns. |
| NFR-02 | Testability | Backend covered by Pytest; frontend by Vitest and React Testing Library; integration tests for status transitions. |
| NFR-03 | API Design | RESTful JSON API documented in `api-contract.md`. |
| NFR-04 | Performance | Responsive UI for hundreds of tickets on a single machine (no distributed scale requirement). |
| NFR-05 | Portability | Runs locally on macOS/Linux/Windows with documented setup. |
| NFR-06 | Security (Core) | No hardcoded secrets; `.env` for configuration; input validation on all write endpoints. |
| NFR-07 | Observability | Structured error responses; optional logging hooks for debugging. |
| NFR-08 | Documentation | Planning artifacts, API contract, data model, and test strategy maintained in repo root. |

---

## 4. Assumptions

| ID | Assumption |
|----|------------|
| A-01 | Single-tenant deployment; no multi-organization isolation required. |
| A-02 | All seeded users may perform all ticket operations in Core (no role-based restrictions unless Stretch). |
| A-03 | `priority` values: `Low`, `Medium`, `High` (or similar fixed enum—confirm in API contract). |
| A-04 | `role` on User is informational in Core; not used for authorization unless Stretch. |
| A-05 | Timestamps stored in UTC; displayed in local time on frontend. |
| A-06 | CSV export includes tickets where `createdBy` matches acting user, regardless of assignee. |
| A-07 | Comment editing/deletion is out of Core scope. |
| A-08 | Ticket deletion is out of Core scope. |
| A-09 | One SQLite database file for development and demo. |
| A-10 | English-only UI and error messages. |

---

## 5. Product Owner Clarification Questions

| # | Question | Impact if Unanswered |
|---|----------|----------------------|
| Q-01 | Should assignee be nullable (unassigned tickets)? | Default: yes, `assignedTo` optional. |
| Q-02 | Can any acting user update any ticket, or only creator/assignee? | Default: any seeded user (Core). |
| Q-03 | Exact priority enum values? | Default: Low, Medium, High. |
| Q-04 | Exact user role enum values? | Default: Agent, Admin (informational). |
| Q-05 | Should status be updatable via the same PATCH as other fields, or a dedicated endpoint? | Affects API design; recommend dedicated `PATCH /tickets/{id}/status`. |
| Q-06 | CSV column set and filename convention? | Define in API contract. |
| Q-07 | Search: full-text on title+description or title only? | Default: title + description. |
| Q-08 | Should list endpoint support pagination in Core? | Default: optional Stretch; return all for small datasets in Core. |
| Q-09 | Is `Closed` terminal? Can tickets reopen? | Default: Closed is terminal; no reopen in Core. |
| Q-10 | Timezone for `createdAt`/`updatedAt` in CSV? | Default: ISO 8601 UTC. |

---

## 6. Edge Cases

| ID | Scenario | Expected Behavior |
|----|----------|-------------------|
| EC-01 | `X-User-Id` missing | `401` or `400` with clear message |
| EC-02 | `X-User-Id` references non-existent user | `401` or `404` with clear message |
| EC-03 | Assignee ID does not exist | `422` validation error |
| EC-04 | Empty title or description on create/update | `422` validation error |
| EC-05 | Invalid priority or status enum | `422` validation error |
| EC-06 | Status transition Open → Resolved (skipping In Progress) | `422` or `409` rejected |
| EC-07 | Status transition Closed → any | Rejected |
| EC-08 | Status transition Cancelled → any | Rejected |
| EC-09 | Comment on non-existent ticket | `404` |
| EC-10 | Update ticket that does not exist | `404` |
| EC-11 | CSV export when user has zero tickets | Valid CSV with headers only |
| EC-12 | Very long title/description | Enforce max length; return validation error |
| EC-13 | Concurrent updates to same ticket | Last write wins (Core); optimistic locking is Stretch |
| EC-14 | Filter returns zero results | Empty list with `200` |
| EC-15 | Special characters in CSV fields | Proper escaping per RFC 4180 |

---

## 7. Out of Scope (Core)

- Real authentication (JWT, OAuth, sessions)
- User registration and profile management
- Role-based access control enforcement
- Email notifications
- File attachments on tickets
- Ticket deletion
- Comment edit/delete
- Real-time updates (WebSockets)
- Production deployment and CI/CD (documented as Stretch)

---

## 8. Traceability

| Requirement Area | Primary Artifacts |
|------------------|-------------------|
| API behavior | `api-contract.md` |
| Data shapes | `data-model.md` |
| UI behavior | `ui-flow.md` |
| Verification | `acceptance-criteria.md`, `test-strategy.md` |
