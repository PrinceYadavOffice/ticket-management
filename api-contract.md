# API Contract

**Version:** 1.0  
**Last Updated:** 2026-07-20  
**Base URL:** `http://localhost:8000`  
**Status:** Design complete — ready for M2/M3 implementation

---

## 1. Conventions

### Content types

| Usage | Content-Type |
|-------|--------------|
| Request/response JSON | `application/json` |
| CSV export | `text/csv; charset=utf-8` |

### JSON field naming

Request and response bodies use **camelCase** (`assignedTo`, `createdAt`). Database uses snake_case internally.

### Acting-user header

```
X-User-Id: <positive integer>
```

Identifies the **acting user** for the request. This is **acting-user context**, not authentication.

| Endpoint | Header required? |
|----------|------------------|
| `GET /health` | No |
| `GET /users` | No (bootstrap for user selector) |
| All others | **Yes** |

### Timestamps

ISO 8601 UTC with `Z` suffix: `"2026-07-20T09:30:00Z"`

### Enums

**TicketPriority:** `Low` | `Medium` | `High` | `Critical`

**TicketStatus:** `Open` | `In Progress` | `Resolved` | `Closed` | `Cancelled`

**UserRole:** `Agent` | `Admin`

---

## 2. Error Response Format

All error responses use this envelope:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Readable error message",
    "details": {}
  }
}
```

### Standard error codes

| HTTP | Code | When |
|------|------|------|
| 400 | `BAD_REQUEST` | Malformed request |
| 401 | `MISSING_ACTING_USER` | `X-User-Id` header absent |
| 401 | `INVALID_ACTING_USER` | Header not a valid integer |
| 401 | `ACTING_USER_NOT_FOUND` | User ID does not exist |
| 404 | `NOT_FOUND` | Ticket or resource not found |
| 422 | `VALIDATION_ERROR` | Pydantic / field validation failed |
| 422 | `INVALID_STATUS_TRANSITION` | State machine rejected transition |
| 500 | `INTERNAL_ERROR` | Unexpected server error |

### Example: validation error

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "fields": {
        "title": "String should have at least 1 character",
        "priority": "Input should be 'Low', 'Medium', 'High' or 'Critical'"
      }
    }
  }
}
```

### Example: invalid status transition

```json
{
  "error": {
    "code": "INVALID_STATUS_TRANSITION",
    "message": "Cannot transition from Open to Resolved",
    "details": {
      "currentStatus": "Open",
      "requestedStatus": "Resolved",
      "allowedTransitions": ["In Progress", "Cancelled"]
    }
  }
}
```

---

## 3. Shared Object Shapes

### User

```json
{
  "id": 1,
  "name": "Alice Agent",
  "email": "alice@example.com",
  "role": "Agent"
}
```

### Ticket (summary — list/create/update/status responses)

```json
{
  "id": 1,
  "title": "Login issue",
  "description": "Cannot reset password",
  "priority": "High",
  "status": "Open",
  "assignedTo": 2,
  "createdBy": 1,
  "createdAt": "2026-07-20T10:00:00Z",
  "updatedAt": "2026-07-20T10:00:00Z"
}
```

`assignedTo` may be `null`.

### Comment

```json
{
  "id": 1,
  "ticketId": 1,
  "message": "Investigating",
  "createdBy": 2,
  "createdAt": "2026-07-20T11:00:00Z"
}
```

### TicketDetail

Ticket object plus `comments` array (ordered by `createdAt` ascending):

```json
{
  "id": 1,
  "title": "...",
  "description": "...",
  "priority": "High",
  "status": "Open",
  "assignedTo": null,
  "createdBy": 1,
  "createdAt": "2026-07-20T10:00:00Z",
  "updatedAt": "2026-07-20T10:00:00Z",
  "comments": [ /* Comment[] */ ],
  "allowedStatusTransitions": ["In Progress", "Cancelled"]
}
```

`allowedStatusTransitions` is computed by the status machine service for UI convenience.

---

## 4. Endpoints

---

### 4.1 Health Check

#### `GET /health`

| | |
|---|---|
| **Purpose** | Verify API is running |
| **Auth header** | Not required |

**Request:** No body. No query parameters.

**Response 200:**

```json
{
  "status": "ok"
}
```

**Validation:** None.

**Errors:** None expected.

---

### 4.2 List Seeded Users

#### `GET /users`

| | |
|---|---|
| **Purpose** | Return all seeded users for the frontend acting-user selector |
| **Auth header** | Not required (bootstrap) |

**Request:** No body. No query parameters.

**Response 200:**

```json
[
  {
    "id": 1,
    "name": "Alice Agent",
    "email": "alice@example.com",
    "role": "Agent"
  },
  {
    "id": 2,
    "name": "Bob Admin",
    "email": "bob@example.com",
    "role": "Admin"
  }
]
```

**Validation:** None.

**Errors:**

| Status | Code | When |
|--------|------|------|
| 500 | `INTERNAL_ERROR` | Database failure |

---

### 4.3 Create Ticket

#### `POST /tickets`

| | |
|---|---|
| **Purpose** | Create a new ticket with status `Open` |
| **Auth header** | Required |

**Request body:**

```json
{
  "title": "Cannot log in",
  "description": "Password reset email never arrives",
  "priority": "High",
  "assignedTo": 2
}
```

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `title` | string | Yes | 1–200 characters, trimmed non-empty |
| `description` | string | Yes | 1–5000 characters, trimmed non-empty |
| `priority` | string | Yes | One of: `Low`, `Medium`, `High`, `Critical` |
| `assignedTo` | integer \| null | No | If provided, must reference existing user |

**Response 201:** Ticket summary object. `status` is always `Open`. `createdBy` is set from `X-User-Id`. `createdAt` and `updatedAt` are equal.

**Validation:**

- Reject unknown fields if strict mode enabled, or ignore extras.
- `status` must **not** appear in request body — if present, return `422` `VALIDATION_ERROR`.

**Errors:**

| Status | Code | When |
|--------|------|------|
| 401 | `MISSING_ACTING_USER` | Header missing |
| 401 | `ACTING_USER_NOT_FOUND` | Invalid user ID |
| 422 | `VALIDATION_ERROR` | Field validation failed |
| 422 | `VALIDATION_ERROR` | `assignedTo` references non-existent user (`details.fields.assignedTo`) |

---

### 4.4 List, Search, and Filter Tickets

#### `GET /tickets`

| | |
|---|---|
| **Purpose** | Return tickets matching optional filters (AND logic) |
| **Auth header** | Required |

**Query parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | string | No | Exact status match |
| `priority` | string | No | Exact priority match |
| `assignedTo` | integer | No | Exact assignee user ID |
| `unassigned` | boolean | No | If `true`, only tickets with null assignee |
| `createdBy` | integer | No | Exact creator user ID |
| `q` | string | No | Case-insensitive substring match in title **or** description |

All provided filters are combined with **AND**. Default sort: `updatedAt` descending.

**Request:** No body.

**Response 200:**

```json
[
  { /* Ticket summary */ }
]
```

Empty array if no matches.

**Validation:**

- Invalid enum value for `status` or `priority` → `422` `VALIDATION_ERROR`
- `assignedTo` / `createdBy` must be positive integers if provided
- `unassigned=true` with `assignedTo` set → `422` `VALIDATION_ERROR` (conflicting filters)

**Errors:**

| Status | Code | When |
|--------|------|------|
| 401 | `MISSING_ACTING_USER` | Header missing |
| 401 | `ACTING_USER_NOT_FOUND` | Invalid user ID |
| 422 | `VALIDATION_ERROR` | Invalid query parameter |

---

### 4.5 Get Ticket Details

#### `GET /tickets/{ticketId}`

| | |
|---|---|
| **Purpose** | Return one ticket with comments and allowed status transitions |
| **Auth header** | Required |

**Path parameters:**

| Param | Type | Validation |
|-------|------|------------|
| `ticketId` | integer | Positive integer |

**Request:** No body.

**Response 200:** TicketDetail object (see §3).

**Validation:** `ticketId` must be a valid integer.

**Errors:**

| Status | Code | When |
|--------|------|------|
| 401 | `MISSING_ACTING_USER` | Header missing |
| 404 | `NOT_FOUND` | Ticket does not exist (`details: { resource: "ticket", id }`) |
| 422 | `VALIDATION_ERROR` | Invalid `ticketId` format |

---

### 4.6 Update Ticket Fields

#### `PATCH /tickets/{ticketId}`

| | |
|---|---|
| **Purpose** | Update title, description, priority, and/or assignee |
| **Auth header** | Required |
| **Restriction** | **Must not** update `status` — use `PATCH /tickets/{ticketId}/status` |

**Path parameters:** `ticketId` (integer)

**Request body** (at least one field required):

```json
{
  "title": "Updated title",
  "description": "Updated description",
  "priority": "Critical",
  "assignedTo": null
}
```

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `title` | string | No* | 1–200 chars if provided |
| `description` | string | No* | 1–5000 chars if provided |
| `priority` | string | No* | Valid priority enum |
| `assignedTo` | integer \| null | No* | Existing user or `null` to unassign |

\*At least one field must be present.

**Response 200:** Updated Ticket summary. `updatedAt` refreshed.

**Validation:**

- Empty PATCH body → `422` `VALIDATION_ERROR`
- If `status` is included → `422` `VALIDATION_ERROR` with message "Status cannot be updated via this endpoint"
- `assignedTo` non-null must reference existing user

**Errors:**

| Status | Code | When |
|--------|------|------|
| 401 | `MISSING_ACTING_USER` | Header missing |
| 404 | `NOT_FOUND` | Ticket not found |
| 422 | `VALIDATION_ERROR` | Field validation or status in body |

---

### 4.7 Transition Ticket Status

#### `PATCH /tickets/{ticketId}/status`

| | |
|---|---|
| **Purpose** | Change ticket status via the state machine |
| **Auth header** | Required |
| **Implementation** | `services/status_machine.py` |

**Path parameters:** `ticketId` (integer)

**Request body:**

```json
{
  "status": "In Progress"
}
```

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `status` | string | Yes | Valid TicketStatus enum + allowed transition |

**Response 200:** Updated Ticket summary with new `status` and `updatedAt`.

**Allowed transitions:**

| From | To |
|------|-----|
| Open | In Progress, Cancelled |
| In Progress | Resolved, Cancelled |
| Resolved | Closed |
| Closed | *(none)* |
| Cancelled | *(none)* |

**Errors:**

| Status | Code | When |
|--------|------|------|
| 401 | `MISSING_ACTING_USER` | Header missing |
| 404 | `NOT_FOUND` | Ticket not found |
| 422 | `VALIDATION_ERROR` | Invalid status enum value |
| 422 | `INVALID_STATUS_TRANSITION` | Transition not allowed |

---

### 4.8 Add Comment

#### `POST /tickets/{ticketId}/comments`

| | |
|---|---|
| **Purpose** | Add a comment to a ticket |
| **Auth header** | Required |

**Path parameters:** `ticketId` (integer)

**Request body:**

```json
{
  "message": "Customer confirmed the issue is resolved on their end."
}
```

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `message` | string | Yes | 1–2000 characters, trimmed non-empty |

**Response 201:** Comment object. `createdBy` from `X-User-Id`. Ticket `updatedAt` is **not** updated (comments are append-only metadata).

**Errors:**

| Status | Code | When |
|--------|------|------|
| 401 | `MISSING_ACTING_USER` | Header missing |
| 404 | `NOT_FOUND` | Ticket not found |
| 422 | `VALIDATION_ERROR` | Empty or too-long message |

---

### 4.9 Export Current User's Tickets as CSV

#### `GET /tickets/export`

| | |
|---|---|
| **Purpose** | Download CSV of all tickets **created by** the acting user |
| **Auth header** | Required |

**Request:** No body. No query parameters.

**Response 200:**

| Header | Value |
|--------|-------|
| `Content-Type` | `text/csv; charset=utf-8` |
| `Content-Disposition` | `attachment; filename="my-tickets-{userId}-{YYYYMMDD}.csv"` |

**CSV columns (header row):**

```
id,title,description,priority,status,assignedTo,createdBy,createdAt,updatedAt
```

- Only tickets where `created_by_user_id` = acting user ID.
- `assignedTo` empty string if null.
- RFC 4180 escaping for fields containing commas, quotes, or newlines.
- If no tickets: header row only.

**Validation:** None beyond acting-user header.

**Errors:**

| Status | Code | When |
|--------|------|------|
| 401 | `MISSING_ACTING_USER` | Header missing |
| 401 | `ACTING_USER_NOT_FOUND` | Invalid user ID |

---

## 5. Status Transition Matrix

| From ↓ / To → | In Progress | Resolved | Closed | Cancelled |
|---------------|:-----------:|:--------:|:------:|:---------:|
| **Open** | ✓ | ✗ | ✗ | ✓ |
| **In Progress** | ✗ | ✓ | ✗ | ✓ |
| **Resolved** | ✗ | ✗ | ✓ | ✗ |
| **Closed** | ✗ | ✗ | ✗ | ✗ |
| **Cancelled** | ✗ | ✗ | ✗ | ✗ |

---

## 6. Endpoint Summary

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Health check |
| GET | `/users` | List seeded users |
| POST | `/tickets` | Create ticket |
| GET | `/tickets` | List / search / filter |
| GET | `/tickets/export` | Export acting user's tickets as CSV |
| GET | `/tickets/{ticketId}` | Ticket detail + comments |
| PATCH | `/tickets/{ticketId}` | Update fields (not status) |
| PATCH | `/tickets/{ticketId}/status` | Status transition |
| POST | `/tickets/{ticketId}/comments` | Add comment |

> **Route ordering note:** Register `GET /tickets/export` before `GET /tickets/{ticketId}` in FastAPI to avoid `export` being parsed as an ID.

---

## 7. Implementation Status

| Endpoint | Status |
|----------|--------|
| All | Not implemented — design complete |
