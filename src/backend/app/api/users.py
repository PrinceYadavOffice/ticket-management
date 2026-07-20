"""User API routes."""

from fastapi import APIRouter

from app.core.dependencies import DbSession
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
def list_users(db: DbSession) -> list[User]:
    return db.query(User).order_by(User.id).all()
