"""User schemas."""

from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str


class UserSummary(BaseModel):
    """Embedded user reference in ticket/comment responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str
