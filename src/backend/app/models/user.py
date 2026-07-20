"""User model."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False)

    created_tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket",
        foreign_keys="Ticket.created_by_user_id",
        back_populates="creator",
    )
    assigned_tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket",
        foreign_keys="Ticket.assigned_to_user_id",
        back_populates="assignee",
    )
    comments: Mapped[list["Comment"]] = relationship(back_populates="author")
