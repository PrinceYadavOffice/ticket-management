"""Database seed script — idempotent, repeatable."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import func, select

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.enums import TicketPriority, TicketStatus
from app.models import Comment, Ticket, User

_REPO_ROOT = Path(__file__).resolve().parents[4]
_USERS_FILE = _REPO_ROOT / "database" / "seed-data" / "users.json"
_SAMPLE_FILE = _REPO_ROOT / "database" / "seed-data" / "sample_data.json"


def _load_json(path: Path) -> list | dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def seed_users(db) -> dict[str, User]:
    users_data = _load_json(_USERS_FILE)
    email_to_user: dict[str, User] = {}
    for entry in users_data:
        existing = db.scalar(select(User).where(User.email == entry["email"]))
        if existing:
            email_to_user[existing.email] = existing
            continue
        user = User(name=entry["name"], email=entry["email"], role=entry["role"])
        db.add(user)
        db.flush()
        email_to_user[user.email] = user
    db.commit()
    return email_to_user


def seed_tickets_and_comments(db, users: dict[str, User]) -> None:
    if not _SAMPLE_FILE.exists():
        return
    sample = _load_json(_SAMPLE_FILE)
    title_to_ticket: dict[str, Ticket] = {}

    for entry in sample.get("tickets", []):
        creator = users.get(entry["created_by_email"])
        if creator is None:
            continue
        existing = db.scalar(select(Ticket).where(Ticket.title == entry["title"]))
        if existing:
            title_to_ticket[existing.title] = existing
            continue
        assignee = users.get(entry["assigned_to_email"]) if entry.get("assigned_to_email") else None
        try:
            priority = TicketPriority(entry["priority"]).value
            status = TicketStatus(entry["status"]).value
        except ValueError as exc:
            print(f"Skipping ticket {entry['title']!r}: invalid priority/status — {exc}", file=sys.stderr)
            continue
        now = datetime.now(timezone.utc)
        ticket = Ticket(
            title=entry["title"],
            description=entry["description"],
            priority=priority,
            status=status,
            assigned_to_user_id=assignee.id if assignee else None,
            created_by_user_id=creator.id,
            created_at=now,
            updated_at=now,
        )
        db.add(ticket)
        db.flush()
        title_to_ticket[ticket.title] = ticket

    db.commit()

    for title, ticket in list(title_to_ticket.items()):
        if ticket.id is None:
            refetched = db.scalar(select(Ticket).where(Ticket.title == title))
            if refetched:
                title_to_ticket[title] = refetched

    for entry in sample.get("comments", []):
        ticket = title_to_ticket.get(entry["ticket_title"])
        if ticket is None:
            ticket = db.scalar(select(Ticket).where(Ticket.title == entry["ticket_title"]))
        author = users.get(entry["author_email"])
        if ticket is None or author is None:
            continue
        exists = db.scalar(
            select(Comment).where(
                Comment.ticket_id == ticket.id,
                Comment.message == entry["message"],
                Comment.created_by_user_id == author.id,
            )
        )
        if exists:
            continue
        db.add(
            Comment(
                ticket_id=ticket.id,
                message=entry["message"],
                created_by_user_id=author.id,
                created_at=datetime.now(timezone.utc),
            )
        )
    db.commit()


def run_seed() -> None:
    settings.ensure_data_dir()
    db = SessionLocal()
    try:
        users = seed_users(db)
        seed_tickets_and_comments(db, users)
        user_count = db.scalar(select(func.count()).select_from(User))
        ticket_count = db.scalar(select(func.count()).select_from(Ticket))
        comment_count = db.scalar(select(func.count()).select_from(Comment))
        print(f"Seed complete: {user_count} users, {ticket_count} tickets, {comment_count} comments")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
    sys.exit(0)
