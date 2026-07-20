"""Comment business logic."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import AppError
from app.models.comment import Comment
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentWithAuthor


def create_comment(
    db: Session,
    ticket_id: int,
    payload: CommentCreate,
    acting_user: User,
) -> CommentWithAuthor:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise AppError(
            "NOT_FOUND",
            f"Ticket with id {ticket_id} does not exist",
            details={"resource": "ticket", "id": ticket_id},
            status_code=404,
        )

    comment = Comment(
        ticket_id=ticket_id,
        message=payload.message,
        created_by_user_id=acting_user.id,
        created_at=datetime.now(timezone.utc),
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    comment = (
        db.query(Comment)
        .options(joinedload(Comment.author))
        .filter(Comment.id == comment.id)
        .one()
    )
    return _to_comment_with_author(comment)


def _to_comment_with_author(comment: Comment) -> CommentWithAuthor:
    return CommentWithAuthor(
        id=comment.id,
        ticket_id=comment.ticket_id,
        message=comment.message,
        created_at=comment.created_at,
        created_by=comment.author,
    )
