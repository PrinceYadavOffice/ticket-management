"""Comment schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.user import UserSummary


class CommentCreate(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)

    @field_validator("message")
    @classmethod
    def message_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Message must not be blank")
        return stripped


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    ticket_id: int = Field(
        validation_alias="ticket_id",
        serialization_alias="ticketId",
    )
    message: str
    created_by: int = Field(
        validation_alias="created_by_user_id",
        serialization_alias="createdBy",
    )
    created_at: datetime = Field(
        validation_alias="created_at",
        serialization_alias="createdAt",
    )


class CommentWithAuthor(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    ticket_id: int = Field(serialization_alias="ticketId")
    message: str
    created_at: datetime = Field(serialization_alias="createdAt")
    created_by: UserSummary = Field(serialization_alias="createdBy")
