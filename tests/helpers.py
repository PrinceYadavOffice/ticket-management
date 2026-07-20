"""Shared test utilities."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.ticket import Ticket


def acting_user_header(user_id: int) -> dict[str, str]:
    return {"X-User-Id": str(user_id)}


def assert_error(response, status_code: int, code: str) -> dict[str, Any]:
    assert response.status_code == status_code, response.text
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == code
    assert "message" in body["error"]
    assert "details" in body["error"]
    return body["error"]


def create_ticket_via_api(
    client: TestClient,
    user_id: int,
    *,
    title: str = "Test ticket",
    description: str = "Test description",
    priority: str = "Medium",
    assigned_to: int | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "title": title,
        "description": description,
        "priority": priority,
    }
    if assigned_to is not None:
        payload["assignedTo"] = assigned_to
    response = client.post(
        "/api/tickets",
        headers=acting_user_header(user_id),
        json=payload,
    )
    assert response.status_code == 201, response.text
    return response.json()


def add_ticket_row(
    db_session: Session,
    *,
    title: str,
    description: str,
    priority: str = "Medium",
    status: str = "Open",
    created_by_user_id: int,
    assigned_to_user_id: int | None = None,
) -> Ticket:
    now = datetime.now(timezone.utc)
    ticket = Ticket(
        title=title,
        description=description,
        priority=priority,
        status=status,
        created_by_user_id=created_by_user_id,
        assigned_to_user_id=assigned_to_user_id,
        created_at=now,
        updated_at=now,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)
    return ticket


def transition_status(client: TestClient, ticket_id: int, status: str):
    return client.patch(f"/api/tickets/{ticket_id}/status", json={"status": status})


def reload_ticket(db_session: Session, ticket_id: int) -> Ticket:
    ticket = db_session.get(Ticket, ticket_id)
    assert ticket is not None
    db_session.refresh(ticket)
    return ticket
