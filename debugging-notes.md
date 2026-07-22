# Debugging Notes

Log issues encountered during development and their resolutions.

## Template

### `[DATE]` — `[SHORT_TITLE]`

**Symptom:**  
**Environment:**  
**Steps to reproduce:**  
**Root cause:**  
**Fix:**  
**Prevention:**

---

## Entries

### 2026-07-22 — PATCH ticket validation returns 500

**Symptom:** Updating a ticket with invalid data (blank title, bad priority, malformed JSON) returned HTTP 500 `INTERNAL_ERROR` instead of 422 `VALIDATION_ERROR`.

**Environment:** macOS, FastAPI 0.2.0, `PATCH /api/tickets/{id}`

**Steps to reproduce:**
```bash
curl -X PATCH http://localhost:8000/api/tickets/7 \
  -H "Content-Type: application/json" \
  -d '{"title":"   "}'
# Before fix: HTTP 500
```

**Investigation:** Route reads raw JSON and calls `TicketUpdate.model_validate(raw_body)` manually to support `assignedTo: null` and forbidden-field checks. Pydantic raises `ValidationError` outside FastAPI's `RequestValidationError` path.

**AI suggestion:** Register global handlers for `pydantic.ValidationError` and `json.JSONDecodeError` returning the standard error envelope with HTTP 422.

**Validation:** Re-ran curl and added regression tests in `tests/backend/test_ticket_detail_update.py`.

**Root cause:** Unhandled `ValidationError` / `JSONDecodeError` fell through to the generic `Exception` handler.

**Fix:** `src/backend/app/core/exceptions.py` — added handlers mirroring `RequestValidationError` field mapping.

**Regression tests:**
- `test_blank_title_on_patch_returns_422`
- `test_invalid_priority_on_patch_returns_422`
- `test_malformed_json_on_patch_returns_422`

**Prevention:** Prefer FastAPI body models where possible; when manual validation is required, ensure all parsing exceptions map to contract error codes.

---

### 2026-07-22 — Comment text lost on failed submit

**Symptom:** User's comment disappeared from the textarea when the API rejected the request.

**Environment:** React frontend, `TicketDetailPage` + `CommentForm`

**Steps to reproduce:** Post a comment that fails server validation or network error; observe empty textarea.

**Root cause:** `CommentForm` called `setMessage('')` synchronously after `onSubmit()` without awaiting the async handler.

**Fix:** `await onSubmit(trimmed)`; clear only on success; `TicketDetailPage.handleComment` rethrows after setting `commentError`.

**Regression tests:** `CommentForm.test.tsx` — `keeps message when submit handler rejects`.

---

### 2026-07-20 — Comprehensive test suite added

**Symptom:** N/A — proactive test expansion  
**Environment:** Pytest with isolated `tmp_path` SQLite per test  
**Steps:** Ran `pytest tests -v` from repo root  
**Root cause:** N/A  
**Fix:** N/A — 65/65 tests passed at time; now 68 after review fixes  
**Prevention:** Keep `tests/helpers.py` utilities; never point tests at `data/tickets.db`

---

### 2026-07-20 — Pydantic ORM field mapping (earlier session)

**Symptom:** `TicketResponse.model_validate(ticket)` failed — `assigned_to` / `created_by` missing  
**Root cause:** SQLAlchemy columns named `assigned_to_user_id` / `created_by_user_id`  
**Fix:** Added `validation_alias` on Pydantic fields in `app/schemas/ticket.py`  
**Prevention:** Always map DB column names explicitly when they differ from API field names

---

### 2026-07-18 — Initial scaffold

**Symptom:** N/A  
**Notes:** Repository created with planning artifacts only.
