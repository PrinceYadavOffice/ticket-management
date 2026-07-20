"""CSV export for acting user's created tickets."""

import csv
import io
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.comment import Comment
from app.models.ticket import Ticket
from app.models.user import User

_CSV_HEADERS = [
    "id",
    "title",
    "description",
    "priority",
    "status",
    "assignedUser",
    "creator",
    "createdAt",
    "updatedAt",
    "commentCount",
]

_FORMULA_PREFIXES = ("=", "+", "-", "@")


def _sanitize_csv_cell(value: str) -> str:
    if value and value[0] in _FORMULA_PREFIXES:
        return "'" + value
    return value


def build_tickets_csv(db: Session, acting_user: User) -> tuple[str, str]:
    tickets = (
        db.scalars(
            select(Ticket)
            .where(Ticket.created_by_user_id == acting_user.id)
            .options(joinedload(Ticket.creator), joinedload(Ticket.assignee))
            .order_by(Ticket.updated_at.desc())
        )
        .unique()
        .all()
    )

    ticket_ids = [t.id for t in tickets]
    counts: dict[int, int] = {}
    if ticket_ids:
        rows = db.execute(
            select(Comment.ticket_id, func.count(Comment.id))
            .where(Comment.ticket_id.in_(ticket_ids))
            .group_by(Comment.ticket_id)
        ).all()
        counts = {tid: cnt for tid, cnt in rows}

    buffer = io.StringIO()
    writer = csv.writer(buffer, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(_CSV_HEADERS)

    for ticket in tickets:
        assigned_name = ticket.assignee.name if ticket.assignee else ""
        writer.writerow(
            [
                _sanitize_csv_cell(str(ticket.id)),
                _sanitize_csv_cell(ticket.title),
                _sanitize_csv_cell(ticket.description),
                _sanitize_csv_cell(ticket.priority),
                _sanitize_csv_cell(ticket.status),
                _sanitize_csv_cell(assigned_name),
                _sanitize_csv_cell(ticket.creator.name),
                _sanitize_csv_cell(_format_ts(ticket.created_at)),
                _sanitize_csv_cell(_format_ts(ticket.updated_at)),
                _sanitize_csv_cell(str(counts.get(ticket.id, 0))),
            ]
        )

    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    filename = f"my-tickets-{acting_user.id}-{today}.csv"
    return buffer.getvalue(), filename


def _format_ts(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
