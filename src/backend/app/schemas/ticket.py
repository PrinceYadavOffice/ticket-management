"""Ticket schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.enums import TicketPriority, TicketStatus
from app.schemas.comment import CommentWithAuthor
from app.schemas.user import UserSummary


def _strip_non_empty(value: str, field_name: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{field_name} must not be blank")
    return stripped


class TicketCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=5000)
    priority: TicketPriority
    assigned_to: int | None = Field(default=None, alias="assignedTo")

    @field_validator("title", "description")
    @classmethod
    def not_blank(cls, value: str, info) -> str:
        return _strip_non_empty(value, info.field_name)


class TicketUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1, max_length=5000)
    priority: TicketPriority | None = None
    assigned_to: int | None = Field(default=None, alias="assignedTo")

    @field_validator("title", "description")
    @classmethod
    def not_blank_when_present(cls, value: str | None, info) -> str | None:
        if value is None:
            return value
        return _strip_non_empty(value, info.field_name)


class TicketStatusUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    status: TicketStatus


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    title: str
    description: str
    priority: str
    status: str
    assigned_to: int | None = Field(
        validation_alias="assigned_to_user_id",
        serialization_alias="assignedTo",
    )
    created_by: int = Field(
        validation_alias="created_by_user_id",
        serialization_alias="createdBy",
    )
    created_at: datetime = Field(
        validation_alias="created_at",
        serialization_alias="createdAt",
    )
    updated_at: datetime = Field(
        validation_alias="updated_at",
        serialization_alias="updatedAt",
    )


class TicketDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    title: str
    description: str
    priority: str
    status: str
    assigned_to: int | None = Field(
        validation_alias="assigned_to_user_id",
        serialization_alias="assignedTo",
    )
    created_by: int = Field(
        validation_alias="created_by_user_id",
        serialization_alias="createdBy",
    )
    created_at: datetime = Field(
        validation_alias="created_at",
        serialization_alias="createdAt",
    )
    updated_at: datetime = Field(
        validation_alias="updated_at",
        serialization_alias="updatedAt",
    )
    creator: UserSummary
    assignee: UserSummary | None = None
    comments: list[CommentWithAuthor] = []
    allowed_status_transitions: list[str] = Field(
        default_factory=list, serialization_alias="allowedStatusTransitions"
    )


class TicketListResponse(BaseModel):
    items: list[TicketResponse]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")
