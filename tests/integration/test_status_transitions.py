"""Integration tests for ticket status transitions."""

from datetime import datetime, timezone

from app.models.ticket import Ticket


def _headers(user_id: int) -> dict[str, str]:
    return {"X-User-Id": str(user_id)}


def _create_open_ticket(db_session, alice) -> Ticket:
    ticket = Ticket(
        title="Status test",
        description="Transition testing",
        priority="Medium",
        status="Open",
        created_by_user_id=alice.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)
    return ticket


def _transition(client, ticket_id: int, status: str):
    return client.patch(f"/api/tickets/{ticket_id}/status", json={"status": status})


def test_open_to_in_progress(client, db_session, alice):
    ticket = _create_open_ticket(db_session, alice)
    response = _transition(client, ticket.id, "In Progress")
    assert response.status_code == 200
    assert response.json()["status"] == "In Progress"


def test_in_progress_to_resolved(client, db_session, alice):
    ticket = _create_open_ticket(db_session, alice)
    _transition(client, ticket.id, "In Progress")
    response = _transition(client, ticket.id, "Resolved")
    assert response.status_code == 200
    assert response.json()["status"] == "Resolved"


def test_resolved_to_closed(client, db_session, alice):
    ticket = _create_open_ticket(db_session, alice)
    _transition(client, ticket.id, "In Progress")
    _transition(client, ticket.id, "Resolved")
    response = _transition(client, ticket.id, "Closed")
    assert response.status_code == 200
    assert response.json()["status"] == "Closed"


def test_open_to_cancelled(client, db_session, alice):
    ticket = _create_open_ticket(db_session, alice)
    response = _transition(client, ticket.id, "Cancelled")
    assert response.status_code == 200
    assert response.json()["status"] == "Cancelled"


def test_in_progress_to_cancelled(client, db_session, alice):
    ticket = _create_open_ticket(db_session, alice)
    _transition(client, ticket.id, "In Progress")
    response = _transition(client, ticket.id, "Cancelled")
    assert response.status_code == 200


def test_open_to_resolved_rejected(client, db_session, alice):
    ticket = _create_open_ticket(db_session, alice)
    response = _transition(client, ticket.id, "Resolved")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INVALID_STATUS_TRANSITION"


def test_closed_to_open_rejected(client, db_session, alice):
    ticket = _create_open_ticket(db_session, alice)
    _transition(client, ticket.id, "In Progress")
    _transition(client, ticket.id, "Resolved")
    _transition(client, ticket.id, "Closed")
    response = _transition(client, ticket.id, "Open")
    assert response.status_code == 409


def test_cancelled_to_in_progress_rejected(client, db_session, alice):
    ticket = _create_open_ticket(db_session, alice)
    _transition(client, ticket.id, "Cancelled")
    response = _transition(client, ticket.id, "In Progress")
    assert response.status_code == 409


def test_same_status_rejected(client, db_session, alice):
    ticket = _create_open_ticket(db_session, alice)
    response = _transition(client, ticket.id, "Open")
    assert response.status_code == 409


def test_invalid_status_value_rejected(client, db_session, alice):
    ticket = _create_open_ticket(db_session, alice)
    response = client.patch(f"/api/tickets/{ticket.id}/status", json={"status": "NotAStatus"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
