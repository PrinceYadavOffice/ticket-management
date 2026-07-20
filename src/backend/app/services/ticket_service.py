"""Ticket business logic."""

from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.enums import TicketPriority, TicketStatus
from app.core.exceptions import AppError
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.comment import CommentWithAuthor
from app.schemas.ticket import (
    TicketCreate,
    TicketDetailResponse,
    TicketListResponse,
    TicketResponse,
    TicketStatusUpdate,
    TicketUpdate,
)
from app.services.status_machine import get_allowed_transitions, validate_transition
from app.services.user_service import get_user_or_raise


def create_ticket(db: Session, payload: TicketCreate, acting_user: User) -> TicketResponse:
    if payload.assigned_to is not None:
        get_user_or_raise(db, payload.assigned_to, field="assignedTo")

    now = datetime.now(timezone.utc)
    ticket = Ticket(
        title=payload.title,
        description=payload.description,
        priority=payload.priority.value,
        status=TicketStatus.OPEN.value,
        assigned_to_user_id=payload.assigned_to,
        created_by_user_id=acting_user.id,
        created_at=now,
        updated_at=now,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return TicketResponse.model_validate(ticket)


def list_tickets(
    db: Session,
    *,
    status: str | None = None,
    priority: str | None = None,
    assigned_to: int | None = None,
    unassigned: bool | None = None,
    created_by: int | None = None,
    q: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> TicketListResponse:
    if unassigned and assigned_to is not None:
        raise AppError(
            "VALIDATION_ERROR",
            "Cannot use assignedTo together with unassigned=true",
            details={"fields": {"assignedTo": "Conflicts with unassigned filter"}},
            status_code=422,
        )

    if page < 1:
        raise AppError(
            "VALIDATION_ERROR",
            "page must be >= 1",
            details={"fields": {"page": "Must be >= 1"}},
            status_code=422,
        )
    if page_size < 1 or page_size > 100:
        raise AppError(
            "VALIDATION_ERROR",
            "pageSize must be between 1 and 100",
            details={"fields": {"pageSize": "Must be between 1 and 100"}},
            status_code=422,
        )

    if status is not None:
        _validate_enum(status, TicketStatus, "status")
    if priority is not None:
        _validate_enum(priority, TicketPriority, "priority")

    query = select(Ticket)
    count_query = select(func.count()).select_from(Ticket)

    def apply_filters(stmt):
        if status is not None:
            stmt = stmt.where(Ticket.status == status)
        if priority is not None:
            stmt = stmt.where(Ticket.priority == priority)
        if unassigned:
            stmt = stmt.where(Ticket.assigned_to_user_id.is_(None))
        elif assigned_to is not None:
            stmt = stmt.where(Ticket.assigned_to_user_id == assigned_to)
        if created_by is not None:
            stmt = stmt.where(Ticket.created_by_user_id == created_by)
        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(
                or_(Ticket.title.ilike(pattern), Ticket.description.ilike(pattern))
            )
        return stmt

    query = apply_filters(query)
    count_query = apply_filters(count_query)

    total = db.scalar(count_query) or 0
    offset = (page - 1) * page_size
    tickets = (
        db.scalars(
            query.order_by(Ticket.updated_at.desc()).offset(offset).limit(page_size)
        )
        .unique()
        .all()
    )

    return TicketListResponse(
        items=[TicketResponse.model_validate(t) for t in tickets],
        total=total,
        page=page,
        page_size=page_size,
    )


def get_ticket_detail(db: Session, ticket_id: int) -> TicketDetailResponse:
    ticket = (
        db.query(Ticket)
        .options(
            joinedload(Ticket.creator),
            joinedload(Ticket.assignee),
            joinedload(Ticket.comments).joinedload(Comment.author),
        )
        .filter(Ticket.id == ticket_id)
        .first()
    )
    if ticket is None:
        raise AppError(
            "NOT_FOUND",
            f"Ticket with id {ticket_id} does not exist",
            details={"resource": "ticket", "id": ticket_id},
            status_code=404,
        )

    current_status = TicketStatus(ticket.status)
    comments = [
        CommentWithAuthor(
            id=c.id,
            ticket_id=c.ticket_id,
            message=c.message,
            created_at=c.created_at,
            created_by=c.author,
        )
        for c in sorted(ticket.comments, key=lambda c: c.created_at)
    ]

    return TicketDetailResponse(
        id=ticket.id,
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority,
        status=ticket.status,
        assigned_to=ticket.assigned_to_user_id,
        created_by=ticket.created_by_user_id,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        creator=ticket.creator,
        assignee=ticket.assignee,
        comments=comments,
        allowed_status_transitions=get_allowed_transitions(current_status),
    )


def update_ticket(
    db: Session, ticket_id: int, payload: TicketUpdate, raw_body: dict
) -> TicketResponse:
    """Update ticket fields; supports explicit assignedTo: null via raw body."""
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise AppError(
            "NOT_FOUND",
            f"Ticket with id {ticket_id} does not exist",
            details={"resource": "ticket", "id": ticket_id},
            status_code=404,
        )

    if payload.title is not None:
        ticket.title = payload.title
    if payload.description is not None:
        ticket.description = payload.description
    if payload.priority is not None:
        ticket.priority = payload.priority.value
    if "assignedTo" in raw_body:
        if raw_body["assignedTo"] is None:
            ticket.assigned_to_user_id = None
        elif payload.assigned_to is not None:
            get_user_or_raise(db, payload.assigned_to, field="assignedTo")
            ticket.assigned_to_user_id = payload.assigned_to

    ticket.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(ticket)
    return TicketResponse.model_validate(ticket)


def transition_status(
    db: Session, ticket_id: int, payload: TicketStatusUpdate
) -> TicketResponse:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise AppError(
            "NOT_FOUND",
            f"Ticket with id {ticket_id} does not exist",
            details={"resource": "ticket", "id": ticket_id},
            status_code=404,
        )

    current = TicketStatus(ticket.status)
    validate_transition(current, payload.status)
    ticket.status = payload.status.value
    ticket.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(ticket)
    return TicketResponse.model_validate(ticket)


from app.models.comment import Comment  # noqa: E402


def _validate_enum(value: str, enum_cls: type, field: str) -> None:
    valid = {e.value for e in enum_cls}
    if value not in valid:
        raise AppError(
            "VALIDATION_ERROR",
            f"Invalid {field} value",
            details={"fields": {field: f"Must be one of: {', '.join(sorted(valid))}"}},
            status_code=422,
        )
