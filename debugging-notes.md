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

### 2026-07-20 — Comprehensive test suite added

**Symptom:** N/A — proactive test expansion  
**Environment:** Pytest with isolated `tmp_path` SQLite per test  
**Steps:** Ran `pytest ../../tests -v` from `src/backend/`  
**Root cause:** N/A  
**Fix:** N/A — 65/65 tests passed; no implementation defects found  
**Prevention:** Keep `tests/helpers.py` utilities for consistent error assertions; never point tests at `data/tickets.db`

### 2026-07-20 — Pydantic ORM field mapping (earlier session)

**Symptom:** `TicketResponse.model_validate(ticket)` failed — `assigned_to` / `created_by` missing  
**Root cause:** SQLAlchemy columns named `assigned_to_user_id` / `created_by_user_id`  
**Fix:** Added `validation_alias` on Pydantic fields in `app/schemas/ticket.py`  
**Prevention:** Always map DB column names explicitly when they differ from API field names

### 2026-07-18 — Initial scaffold

**Symptom:** N/A  
**Notes:** Repository created with planning artifacts only.
