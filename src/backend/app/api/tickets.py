"""Ticket API routes."""

from typing import Annotated

from fastapi import APIRouter, Query, Request, Response

from app.core.dependencies import ActingUser, DbSession
from app.core.exceptions import AppError
from app.schemas.comment import CommentCreate, CommentWithAuthor
from app.schemas.ticket import (
    TicketCreate,
    TicketDetailResponse,
    TicketListResponse,
    TicketResponse,
    TicketStatusUpdate,
    TicketUpdate,
)
from app.services import comment_service, csv_export, ticket_service

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("/export.csv")
def export_tickets_csv(db: DbSession, acting_user: ActingUser) -> Response:
    content, filename = csv_export.build_tickets_csv(db, acting_user)
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("", response_model=TicketResponse, status_code=201)
def create_ticket(
    payload: TicketCreate,
    db: DbSession,
    acting_user: ActingUser,
) -> TicketResponse:
    return ticket_service.create_ticket(db, payload, acting_user)


@router.get("", response_model=TicketListResponse)
def list_tickets(
    db: DbSession,
    status: Annotated[str | None, Query()] = None,
    priority: Annotated[str | None, Query()] = None,
    assigned_to: Annotated[int | None, Query(alias="assignedTo")] = None,
    unassigned: Annotated[bool | None, Query()] = None,
    created_by: Annotated[int | None, Query(alias="createdBy")] = None,
    q: Annotated[str | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
) -> TicketListResponse:
    return ticket_service.list_tickets(
        db,
        status=status,
        priority=priority,
        assigned_to=assigned_to,
        unassigned=unassigned,
        created_by=created_by,
        q=q,
        page=page,
        page_size=page_size,
    )


@router.get("/{ticket_id}", response_model=TicketDetailResponse)
def get_ticket(ticket_id: int, db: DbSession) -> TicketDetailResponse:
    return ticket_service.get_ticket_detail(db, ticket_id)


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: int,
    request: Request,
    db: DbSession,
) -> TicketResponse:
    raw_body = await request.json()
    if "status" in raw_body:
        raise AppError(
            "VALIDATION_ERROR",
            "Status cannot be updated via this endpoint",
            details={"fields": {"status": "Use PATCH /api/tickets/{ticketId}/status"}},
            status_code=422,
        )
    for forbidden in ("createdBy", "createdAt", "updatedAt"):
        if forbidden in raw_body:
            raise AppError(
                "VALIDATION_ERROR",
                f"{forbidden} cannot be updated via this endpoint",
                details={"fields": {forbidden: "Field is read-only"}},
                status_code=422,
            )
    if not raw_body:
        raise AppError(
            "VALIDATION_ERROR",
            "At least one field must be provided",
            details={"fields": {"body": "Request body cannot be empty"}},
            status_code=422,
        )
    payload = TicketUpdate.model_validate(raw_body)
    if (
        payload.title is None
        and payload.description is None
        and payload.priority is None
        and "assignedTo" not in raw_body
    ):
        raise AppError(
            "VALIDATION_ERROR",
            "At least one field must be provided",
            details={"fields": {"body": "No updatable fields provided"}},
            status_code=422,
        )
    return ticket_service.update_ticket(db, ticket_id, payload, raw_body)


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def update_ticket_status(
    ticket_id: int,
    payload: TicketStatusUpdate,
    db: DbSession,
) -> TicketResponse:
    return ticket_service.transition_status(db, ticket_id, payload)


@router.post("/{ticket_id}/comments", response_model=CommentWithAuthor, status_code=201)
def add_comment(
    ticket_id: int,
    payload: CommentCreate,
    db: DbSession,
    acting_user: ActingUser,
) -> CommentWithAuthor:
    return comment_service.create_comment(db, ticket_id, payload, acting_user)
