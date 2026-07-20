# API Contract

**Version:** 1.1 (Implemented)  
**Last Updated:** 2026-07-20  
**Base URL:** `http://localhost:8000`

---

## 1. Conventions

- JSON bodies and responses use **camelCase**
- Error envelope on all failures:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Readable error message",
    "details": {}
  }
}
```

### Acting-user header

```
X-User-Id: <positive integer>
```

**Acting-user context — not authentication.**

| Endpoint | X-User-Id required |
|----------|-------------------|
| `GET /health` | No |
| `GET /api/users` | No |
| `POST /api/tickets` | **Yes** |
| `GET /api/tickets` | No |
| `GET /api/tickets/{ticketId}` | No |
| `PATCH /api/tickets/{ticketId}` | No |
| `PATCH /api/tickets/{ticketId}/status` | No |
| `POST /api/tickets/{ticketId}/comments` | **Yes** |
| `GET /api/tickets/export.csv` | **Yes** |

### Enums

- **Priority:** `Low`, `Medium`, `High`, `Critical`
- **Status:** `Open`, `In Progress`, `Resolved`, `Closed`, `Cancelled`
- **Role:** `Agent`, `Admin`

---

## 2. Error Codes

| HTTP | Code | When |
|------|------|------|
| 401 | `MISSING_ACTING_USER` | Header absent |
| 401 | `INVALID_ACTING_USER` | Non-integer header |
| 401 | `ACTING_USER_NOT_FOUND` | User ID not in DB |
| 404 | `NOT_FOUND` | Ticket not found |
| 409 | `INVALID_STATUS_TRANSITION` | State machine rejected transition |
| 422 | `VALIDATION_ERROR` | Input validation failed |
| 500 | `INTERNAL_ERROR` | Unexpected error |

---

## 3. Endpoints

### `GET /health`

| | |
|---|---|
| Purpose | Health check |
| Request | None |
| Response 200 | `{ "status": "ok" }` |

---

### `GET /api/users`

| | |
|---|---|
| Purpose | List seeded users for acting-user selector |
| Request | None |
| Response 200 | `User[]` |

```json
[{ "id": 1, "name": "Alice Chen", "email": "alice.chen@supportdesk.example", "role": "Agent" }]
```

---

### `POST /api/tickets`

| | |
|---|---|
| Purpose | Create ticket (status defaults to `Open`) |
| Headers | `X-User-Id` required |
| Request | `{ title, description, priority, assignedTo? }` |
| Response 201 | `Ticket` |
| Validation | Non-blank title/description; valid priority; valid assignee if set; `status` forbidden |
| Errors | 401 acting user; 422 validation |

---

### `GET /api/tickets`

| | |
|---|---|
| Purpose | List, search, filter tickets with pagination |
| Query params | See table below |
| Response 200 | Paginated list |

| Param | Type | Description |
|-------|------|-------------|
| `status` | string | Exact status filter |
| `priority` | string | Exact priority filter |
| `assignedTo` | int | Assignee user ID |
| `unassigned` | bool | `true` = only unassigned |
| `createdBy` | int | Creator user ID |
| `q` | string | Search title and description (case-insensitive) |
| `page` | int | Page number (default 1) |
| `pageSize` | int | Page size 1–100 (default 20) |

```json
{
  "items": [ { /* Ticket */ } ],
  "total": 42,
  "page": 1,
  "pageSize": 20
}
```

Filters combine with **AND**. Sort: `updatedAt` descending.

---

### `GET /api/tickets/{ticketId}`

| | |
|---|---|
| Purpose | Ticket detail with comments and allowed transitions |
| Response 200 | `TicketDetail` |

```json
{
  "id": 1,
  "title": "...",
  "description": "...",
  "priority": "High",
  "status": "Open",
  "assignedTo": 2,
  "createdBy": 1,
  "createdAt": "2026-07-20T10:00:00Z",
  "updatedAt": "2026-07-20T10:00:00Z",
  "creator": { "id": 1, "name": "...", "email": "...", "role": "Agent" },
  "assignee": { "id": 2, "name": "...", "email": "...", "role": "Admin" },
  "comments": [
    {
      "id": 1,
      "ticketId": 1,
      "message": "...",
      "createdAt": "...",
      "createdBy": { "id": 2, "name": "...", "email": "...", "role": "Admin" }
    }
  ],
  "allowedStatusTransitions": ["In Progress", "Cancelled"]
}
```

Comments ordered chronologically. Errors: 404 not found.

---

### `PATCH /api/tickets/{ticketId}`

| | |
|---|---|
| Purpose | Update title, description, priority, assignee |
| Request | Partial `{ title?, description?, priority?, assignedTo? }` |
| Response 200 | `Ticket` |
| Forbidden fields | `status`, `createdBy`, `createdAt`, `updatedAt` → 422 |
| Notes | `assignedTo: null` unassigns |

---

### `PATCH /api/tickets/{ticketId}/status`

| | |
|---|---|
| Purpose | Status transition via state machine |
| Request | `{ "status": "In Progress" }` |
| Response 200 | `Ticket` |
| Errors | 404 not found; **409** `INVALID_STATUS_TRANSITION`; 422 invalid enum |

**Allowed transitions:**

| From | To |
|------|-----|
| Open | In Progress, Cancelled |
| In Progress | Resolved, Cancelled |
| Resolved | Closed |

Rejected: same-status, from Closed/Cancelled, all unlisted transitions.

---

### `POST /api/tickets/{ticketId}/comments`

| | |
|---|---|
| Purpose | Add comment |
| Headers | `X-User-Id` required |
| Request | `{ "message": "..." }` |
| Response 201 | `CommentWithAuthor` |
| Validation | Non-blank message; ticket must exist |
| Errors | 401, 404, 422 |

---

### `GET /api/tickets/export.csv`

| | |
|---|---|
| Purpose | CSV of tickets **created by** acting user |
| Headers | `X-User-Id` required |
| Response 200 | `text/csv; charset=utf-8` |
| Headers | `Content-Disposition: attachment; filename="my-tickets-{userId}-{YYYYMMDD}.csv"` |

**CSV columns:** `id`, `title`, `description`, `priority`, `status`, `assignedUser`, `creator`, `createdAt`, `updatedAt`, `commentCount`

- RFC 4180 quoting for commas/quotes
- Formula injection mitigation: values starting with `=`, `+`, `-`, `@` prefixed with `'`
- Empty result: header row only

---

## 4. Shared Types

### Ticket (summary)

```json
{
  "id": 1,
  "title": "string",
  "description": "string",
  "priority": "High",
  "status": "Open",
  "assignedTo": 2,
  "createdBy": 1,
  "createdAt": "2026-07-20T10:00:00Z",
  "updatedAt": "2026-07-20T10:00:00Z"
}
```

`assignedTo` may be `null`.

---

## 5. Implementation Status

| Endpoint | Status |
|----------|--------|
| All listed endpoints | **Implemented** |

OpenAPI: `http://localhost:8000/docs`
