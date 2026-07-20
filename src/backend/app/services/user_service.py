"""User lookup helpers."""

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.user import User


def get_user_or_raise(db: Session, user_id: int, *, field: str = "userId") -> User:
    user = db.get(User, user_id)
    if user is None:
        raise AppError(
            "VALIDATION_ERROR",
            f"User with id {user_id} does not exist",
            details={"fields": {field: f"User {user_id} not found"}},
            status_code=422,
        )
    return user
