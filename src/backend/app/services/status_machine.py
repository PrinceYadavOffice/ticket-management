"""Ticket status state machine — pure domain logic."""

from app.core.enums import TicketStatus
from app.core.exceptions import AppError

_ALLOWED: dict[TicketStatus, set[TicketStatus]] = {
    TicketStatus.OPEN: {TicketStatus.IN_PROGRESS, TicketStatus.CANCELLED},
    TicketStatus.IN_PROGRESS: {TicketStatus.RESOLVED, TicketStatus.CANCELLED},
    TicketStatus.RESOLVED: {TicketStatus.CLOSED},
    TicketStatus.CLOSED: set(),
    TicketStatus.CANCELLED: set(),
}


def get_allowed_transitions(current: TicketStatus) -> list[str]:
    return sorted(s.value for s in _ALLOWED.get(current, set()))


def validate_transition(current: TicketStatus, target: TicketStatus) -> None:
    if current == target:
        raise AppError(
            "INVALID_STATUS_TRANSITION",
            f"Ticket is already in status '{current.value}'",
            details={
                "currentStatus": current.value,
                "requestedStatus": target.value,
                "allowedTransitions": get_allowed_transitions(current),
            },
            status_code=409,
        )
    allowed = _ALLOWED.get(current, set())
    if target not in allowed:
        raise AppError(
            "INVALID_STATUS_TRANSITION",
            f"Cannot transition from '{current.value}' to '{target.value}'",
            details={
                "currentStatus": current.value,
                "requestedStatus": target.value,
                "allowedTransitions": get_allowed_transitions(current),
            },
            status_code=409,
        )
