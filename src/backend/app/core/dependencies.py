"""FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AppError
from app.models.user import User


def get_acting_user(
    x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
    db: Session = Depends(get_db),
) -> User:
    if x_user_id is None or not str(x_user_id).strip():
        raise AppError(
            "MISSING_ACTING_USER",
            "Valid X-User-Id header is required",
            status_code=401,
        )
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise AppError(
            "INVALID_ACTING_USER",
            "X-User-Id must be a positive integer",
            status_code=401,
        ) from None
    if user_id < 1:
        raise AppError(
            "INVALID_ACTING_USER",
            "X-User-Id must be a positive integer",
            status_code=401,
        )
    user = db.get(User, user_id)
    if user is None:
        raise AppError(
            "ACTING_USER_NOT_FOUND",
            f"User with id {user_id} does not exist",
            details={"userId": user_id},
            status_code=401,
        )
    return user


DbSession = Annotated[Session, Depends(get_db)]
ActingUser = Annotated[User, Depends(get_acting_user)]
