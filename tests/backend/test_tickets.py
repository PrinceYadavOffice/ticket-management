"""Ticket API tests."""

from datetime import datetime, timezone

from app.models.ticket import Ticket


def _headers(user_id: int) -> dict[str, str]:
    return {"X-User-Id": str(user_id)}


def test_create_ticket_requires_acting_user(client):
    response = client.post("/api/tickets", json={"title": "T", "description": "D", "priority": "Low"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "MISSING_ACTING_USER"


def test_create_ticket_success(client, alice, bob):
    response = client.post(
        "/api/tickets",
        headers=_headers(alice.id),
        json={
            "title": "New issue",
            "description": "Something broke",
            "priority": "High",
            "assignedTo": bob.id,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New issue"
    assert data["status"] == "Open"
    assert data["createdBy"] == alice.id
    assert data["assignedTo"] == bob.id


def test_create_ticket_blank_title_rejected(client, alice):
    response = client.post(
        "/api/tickets",
        headers=_headers(alice.id),
        json={"title": "   ", "description": "Valid", "priority": "Low"},
    )
    assert response.status_code == 422


def test_create_ticket_invalid_assignee(client, alice):
    response = client.post(
        "/api/tickets",
        headers=_headers(alice.id),
        json={"title": "T", "description": "D", "priority": "Low", "assignedTo": 9999},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_list_tickets_pagination(client, alice, db_session):
    for i in range(3):
        db_session.add(
            Ticket(
                title=f"Ticket {i}",
                description=f"Desc {i}",
                priority="Low",
                status="Open",
                created_by_user_id=alice.id,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
        )
    db_session.commit()

    response = client.get("/api/tickets?page=1&pageSize=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["pageSize"] == 2


def test_filter_by_status(client, sample_ticket, db_session, alice):
    db_session.add(
        Ticket(
            title="Closed one",
            description="Done",
            priority="Low",
            status="Closed",
            created_by_user_id=alice.id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )
    db_session.commit()

    response = client.get("/api/tickets?status=Open")
    assert response.status_code == 200
    assert all(t["status"] == "Open" for t in response.json()["items"])


def test_search_query(client, sample_ticket):
    response = client.get("/api/tickets?q=Test")
    assert response.status_code == 200
    assert any("Test" in t["title"] for t in response.json()["items"])


def test_get_ticket_detail(client, sample_ticket, alice, bob):
    response = client.get(f"/api/tickets/{sample_ticket.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_ticket.id
    assert data["creator"]["email"] == alice.email
    assert data["assignee"]["email"] == bob.email
    assert "allowedStatusTransitions" in data


def test_get_ticket_not_found(client):
    response = client.get("/api/tickets/99999")
    assert response.status_code == 404


def test_update_ticket_fields(client, sample_ticket):
    response = client.patch(
        f"/api/tickets/{sample_ticket.id}",
        json={"title": "Updated title", "priority": "Critical"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated title"
    assert response.json()["priority"] == "Critical"


def test_update_ticket_rejects_status(client, sample_ticket):
    response = client.patch(
        f"/api/tickets/{sample_ticket.id}",
        json={"status": "Closed"},
    )
    assert response.status_code == 422
    assert "status" in response.json()["error"]["details"]["fields"]


def test_update_ticket_rejects_created_by(client, sample_ticket):
    response = client.patch(
        f"/api/tickets/{sample_ticket.id}",
        json={"createdBy": 1},
    )
    assert response.status_code == 422


def test_add_comment(client, sample_ticket, bob):
    response = client.post(
        f"/api/tickets/{sample_ticket.id}/comments",
        headers=_headers(bob.id),
        json={"message": "Looking into this"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Looking into this"
    assert data["createdBy"]["id"] == bob.id


def test_add_blank_comment_rejected(client, sample_ticket, bob):
    response = client.post(
        f"/api/tickets/{sample_ticket.id}/comments",
        headers=_headers(bob.id),
        json={"message": "   "},
    )
    assert response.status_code == 422


def test_comments_in_detail_chronological(client, sample_ticket, alice, bob):
    client.post(
        f"/api/tickets/{sample_ticket.id}/comments",
        headers=_headers(alice.id),
        json={"message": "First comment"},
    )
    client.post(
        f"/api/tickets/{sample_ticket.id}/comments",
        headers=_headers(bob.id),
        json={"message": "Second comment"},
    )
    response = client.get(f"/api/tickets/{sample_ticket.id}")
    messages = [c["message"] for c in response.json()["comments"]]
    assert messages == ["First comment", "Second comment"]
