"""Status machine unit tests."""

import pytest

from app.core.enums import TicketStatus
from app.core.exceptions import AppError
from app.services.status_machine import get_allowed_transitions, validate_transition


def test_allowed_from_open():
    assert set(get_allowed_transitions(TicketStatus.OPEN)) == {"Cancelled", "In Progress"}


def test_allowed_from_in_progress():
    assert set(get_allowed_transitions(TicketStatus.IN_PROGRESS)) == {"Cancelled", "Resolved"}


def test_allowed_from_resolved():
    assert get_allowed_transitions(TicketStatus.RESOLVED) == ["Closed"]


def test_terminal_states():
    assert get_allowed_transitions(TicketStatus.CLOSED) == []
    assert get_allowed_transitions(TicketStatus.CANCELLED) == []


def test_valid_transition_open_to_in_progress():
    validate_transition(TicketStatus.OPEN, TicketStatus.IN_PROGRESS)


def test_invalid_same_status():
    with pytest.raises(AppError) as exc:
        validate_transition(TicketStatus.OPEN, TicketStatus.OPEN)
    assert exc.value.status_code == 409
    assert exc.value.code == "INVALID_STATUS_TRANSITION"


def test_invalid_open_to_resolved():
    with pytest.raises(AppError) as exc:
        validate_transition(TicketStatus.OPEN, TicketStatus.RESOLVED)
    assert exc.value.status_code == 409


def test_invalid_from_closed():
    with pytest.raises(AppError) as exc:
        validate_transition(TicketStatus.CLOSED, TicketStatus.OPEN)
    assert exc.value.status_code == 409


def test_invalid_from_cancelled():
    with pytest.raises(AppError) as exc:
        validate_transition(TicketStatus.CANCELLED, TicketStatus.IN_PROGRESS)
    assert exc.value.status_code == 409
