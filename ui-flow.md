# UI Flow

**Version:** 0.1 (Draft)

## Global Layout

```
┌──────────────────────────────────────────────────────┐
│  Support Ticket Management    [Acting as: ▼ User]    │
│  (demo mode — X-User-Id, not authenticated)          │
├──────────────────────────────────────────────────────┤
│  [Tickets]  [Export My Tickets CSV]                  │
├──────────────────────────────────────────────────────┤
│                    <main content>                    │
└──────────────────────────────────────────────────────┘
```

---

## Routes (Planned)

| Path | View | Description |
|------|------|-------------|
| `/` | Ticket List | Default; filters and search |
| `/tickets/new` | Create Ticket | Form for new ticket |
| `/tickets/:id` | Ticket Detail | View/edit, status, comments |

---

## Flow 1: Select Acting User

1. App loads → `GET /users`
2. Selector defaults to first user (or localStorage preference — Stretch)
3. User changes selection → context updates → API client sets `X-User-Id`
4. Banner reminds user this is not real authentication

---

## Flow 2: Create Ticket

1. User clicks "New Ticket"
2. Form: title, description, priority, optional assignee
3. Submit → `POST /tickets`
4. On success → navigate to detail or list
5. On error → show field-level messages from API

---

## Flow 3: List & Filter Tickets

1. `GET /tickets` with query params from filter UI
2. Table/cards: title, status, priority, assignee, updated date
3. Click row → detail view
4. Empty state when no matches

---

## Flow 4: Ticket Detail

1. `GET /tickets/{id}`
2. Display all fields; editable: title, description, priority, assignee
3. Save → `PATCH /tickets/{id}`
4. Status section: buttons only for **allowed** next statuses (from API or client rules mirroring contract)
5. Status change → `PATCH /tickets/{id}/status`
6. Comments list + add form → `POST /tickets/{id}/comments`

---

## Flow 5: Export CSV

1. User clicks "Export My Tickets"
2. `GET /tickets/export` with current `X-User-Id`
3. Browser downloads `my-tickets.csv`

---

## Error States

| Situation | UI Behavior |
|-----------|-------------|
| Network failure | Toast/banner: "Unable to reach server" |
| 422 validation | Inline field errors |
| 404 | "Ticket not found" with link to list |
| Invalid status transition | Alert with API message |

---

## Implementation Status

UI not implemented. Scaffold only in `src/frontend/`.
