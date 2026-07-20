# API Contract

**Version:** 0.1 (Draft)  
**Base URL:** `http://localhost:8000`  
**Content-Type:** `application/json` (unless noted)

## Acting-User Header (Required)

All endpoints except health check require:

```
X-User-Id: <user_id>
```

This header identifies the **acting user** for the request. It is **not** authentication. Missing or invalid values return `401` with:

```json
{ "detail": "Valid X-User-Id header required", "code": "missing_acting_user" }
```

---

## Enums

### TicketStatus

`Open` | `In Progress` | `Resolved` | `Closed` | `Cancelled`

### TicketPriority

`Low` | `Medium` | `High`

### UserRole (informational in Core)

`Agent` | `Admin`

---

## Endpoints

### Health

#### `GET /health`

No `X-User-Id` required.

**Response 200:**

```json
{ "status": "ok" }
```

---

### Users

#### `GET /users`

List seeded users (for frontend selector).

**Response 200:**

```json
[
  { "id": 1, "name": "Alice Agent", "email": "alice@example.com", "role": "Agent" }
]
```

---

### Tickets

#### `GET /tickets`

List tickets with optional filters.

**Query parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `status` | string | Filter by status |
| `priority` | string | Filter by priority |
| `assignedTo` | integer | Filter by assignee user ID |
| `q` | string | Search title and description |

**Response 200:**

```json
[
  {
    "id": 1,
    "title": "Login issue",
    "description": "Cannot reset password",
    "priority": "High",
    "status": "Open",
    "assignedTo": 2,
    "createdBy": 1,
    "createdAt": "2026-07-18T10:00:00Z",
    "updatedAt": "2026-07-18T10:00:00Z"
  }
]
```

#### `POST /tickets`

Create a ticket. Status defaults to `Open`.

**Request body:**

```json
{
  "title": "string (required, 1-200)",
  "description": "string (required, 1-5000)",
  "priority": "Low | Medium | High (required)",
  "assignedTo": 2
}
```

`assignedTo` is optional (nullable).

**Response 201:** Ticket object

**Response 422:** Validation errors

#### `GET /tickets/{id}`

Ticket detail with comments.

**Response 200:**

```json
{
  "id": 1,
  "title": "...",
  "description": "...",
  "priority": "High",
  "status": "Open",
  "assignedTo": 2,
  "createdBy": 1,
  "createdAt": "2026-07-18T10:00:00Z",
  "updatedAt": "2026-07-18T10:00:00Z",
  "comments": [
    {
      "id": 1,
      "ticketId": 1,
      "message": "Investigating",
      "createdBy": 2,
      "createdAt": "2026-07-18T11:00:00Z"
    }
  ]
}
```

**Response 404:** Ticket not found

#### `PATCH /tickets/{id}`

Update title, description, priority, assignee. **Does not change status.**

**Request body (all fields optional):**

```json
{
  "title": "string",
  "description": "string",
  "priority": "Low | Medium | High",
  "assignedTo": 2
}
```

Set `assignedTo` to `null` to unassign.

**Response 200:** Updated ticket

#### `PATCH /tickets/{id}/status`

Change status via state machine.

**Request body:**

```json
{ "status": "In Progress" }
```

**Response 200:** Updated ticket

**Response 422:** Invalid transition

```json
{
  "detail": "Invalid status transition from Open to Resolved",
  "code": "invalid_status_transition"
}
```

#### `GET /tickets/export`

Export CSV of tickets **created by the acting user** (`X-User-Id`).

**Response 200:** `Content-Type: text/csv`

**Headers:**

```
Content-Disposition: attachment; filename="my-tickets.csv"
```

**CSV columns:** `id`, `title`, `description`, `priority`, `status`, `assignedTo`, `createdBy`, `createdAt`, `updatedAt`

---

### Comments

#### `POST /tickets/{id}/comments`

**Request body:**

```json
{ "message": "string (required, 1-2000)" }
```

**Response 201:** Comment object

**Response 404:** Ticket not found

---

## Status Transition Matrix

| From ↓ / To → | In Progress | Resolved | Closed | Cancelled |
|---------------|:-----------:|:--------:|:------:|:---------:|
| Open          | ✓ | ✗ | ✗ | ✓ |
| In Progress   | ✗ | ✓ | ✗ | ✓ |
| Resolved      | ✗ | ✗ | ✓ | ✗ |
| Closed        | ✗ | ✗ | ✗ | ✗ |
| Cancelled     | ✗ | ✗ | ✗ | ✗ |

---

## Implementation Status

| Endpoint | Status |
|----------|--------|
| All | Not implemented (planning draft) |
