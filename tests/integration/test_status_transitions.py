"""Integration tests for ticket status state machine."""

import time
from datetime import datetime, timezone

import pytest

from app.models.ticket import Ticket
from tests.helpers import assert_error, reload_ticket, transition_status


def _create_ticket(db_session, alice, *, status: str = "Open") -> Ticket:
    now = datetime.now(timezone.utc)
    ticket = Ticket(
        title="Status test",
        description="Transition testing",
        priority="Medium",
        status=status,
        created_by_user_id=alice.id,
        created_at=now,
        updated_at=now,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)
    return ticket


def _set_status(client, db_session, ticket: Ticket, status: str) -> Ticket:
    if status == "Open":
        return ticket
    if status == "In Progress":
        transition_status(client, ticket.id, "In Progress")
    elif status == "Resolved":
        transition_status(client, ticket.id, "In Progress")
        transition_status(client, ticket.id, "Resolved")
    elif status == "Closed":
        transition_status(client, ticket.id, "In Progress")
        transition_status(client, ticket.id, "Resolved")
        transition_status(client, ticket.id, "Closed")
    elif status == "Cancelled":
        transition_status(client, ticket.id, "Cancelled")
    else:
        raise ValueError(f"Unsupported setup status: {status}")
    return reload_ticket(db_session, ticket.id)


class TestValidTransitions:
    def test_open_to_in_progress(self, client, db_session, alice):
        ticket = _create_ticket(db_session, alice)
        response = transition_status(client, ticket.id, "In Progress")
        assert response.status_code == 200
        assert response.json()["status"] == "In Progress"

    def test_open_to_cancelled(self, client, db_session, alice):
        ticket = _create_ticket(db_session, alice)
        response = transition_status(client, ticket.id, "Cancelled")
        assert response.status_code == 200
        assert response.json()["status"] == "Cancelled"

    def test_in_progress_to_resolved(self, client, db_session, alice):
        ticket = _create_ticket(db_session, alice)
        _set_status(client, db_session, ticket, "In Progress")
        response = transition_status(client, ticket.id, "Resolved")
        assert response.status_code == 200
        assert response.json()["status"] == "Resolved"

    def test_in_progress_to_cancelled(self, client, db_session, alice):
        ticket = _create_ticket(db_session, alice)
        _set_status(client, db_session, ticket, "In Progress")
        response = transition_status(client, ticket.id, "Cancelled")
        assert response.status_code == 200
        assert response.json()["status"] == "Cancelled"

    def test_resolved_to_closed(self, client, db_session, alice):
        ticket = _create_ticket(db_session, alice)
        _set_status(client, db_session, ticket, "Resolved")
        response = transition_status(client, ticket.id, "Closed")
        assert response.status_code == 200
        assert response.json()["status"] == "Closed"


class TestInvalidTransitions:
    @pytest.mark.parametrize(
        "from_status,attempted",
        [
            ("Open", "Resolved"),
            ("Open", "Closed"),
            ("In Progress", "Closed"),
            ("Resolved", "Open"),
            ("Closed", "Open"),
            ("Cancelled", "Open"),
        ],
    )
    def test_rejected_transitions_do_not_modify_status(
        self, client, db_session, alice, from_status, attempted
    ):
        ticket = _create_ticket(db_session, alice)
        ticket = _set_status(client, db_session, ticket, from_status)
        before_status = reload_ticket(db_session, ticket.id).status
        response = transition_status(client, ticket.id, attempted)
        assert_error(response, 409, "INVALID_STATUS_TRANSITION")
        assert reload_ticket(db_session, ticket.id).status == before_status

    def test_same_status_rejected_and_unchanged(self, client, db_session, alice):
        ticket = _create_ticket(db_session, alice)
        response = transition_status(client, ticket.id, "Open")
        assert_error(response, 409, "INVALID_STATUS_TRANSITION")
        assert reload_ticket(db_session, ticket.id).status == "Open"


class TestTransitionSideEffects:
    def test_successful_transition_updates_updated_at(self, client, db_session, alice):
        ticket = _create_ticket(db_session, alice)
        before = reload_ticket(db_session, ticket.id).updated_at
        time.sleep(0.02)
        response = transition_status(client, ticket.id, "In Progress")
        assert response.status_code == 200
        after = reload_ticket(db_session, ticket.id).updated_at
        assert after >= before

    def test_invalid_status_value_rejected(self, client, db_session, alice):
        ticket = _create_ticket(db_session, alice)
        response = client.patch(
            f"/api/tickets/{ticket.id}/status",
            json={"status": "NotAStatus"},
        )
        assert_error(response, 422, "VALIDATION_ERROR")
        assert reload_ticket(db_session, ticket.id).status == "Open"

    def test_missing_ticket_returns_404(self, client):
        response = transition_status(client, 99999, "In Progress")
        assert_error(response, 404, "NOT_FOUND")
