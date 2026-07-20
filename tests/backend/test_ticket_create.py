"""Ticket creation API tests."""

from tests.helpers import acting_user_header, assert_error, create_ticket_via_api


class TestTicketCreation:
    def test_successful_creation(self, client, alice, bob):
        data = create_ticket_via_api(
            client,
            alice.id,
            title="Login failure",
            description="User cannot sign in",
            priority="High",
            assigned_to=bob.id,
        )
        assert data["title"] == "Login failure"
        assert data["description"] == "User cannot sign in"
        assert data["priority"] == "High"
        assert data["status"] == "Open"
        assert data["createdBy"] == alice.id
        assert data["assignedTo"] == bob.id
        assert "createdAt" in data
        assert "updatedAt" in data

    def test_missing_x_user_id(self, client):
        response = client.post(
            "/api/tickets",
            json={"title": "T", "description": "D", "priority": "Low"},
        )
        assert_error(response, 401, "MISSING_ACTING_USER")

    def test_invalid_x_user_id_non_integer(self, client):
        response = client.post(
            "/api/tickets",
            headers={"X-User-Id": "not-a-number"},
            json={"title": "T", "description": "D", "priority": "Low"},
        )
        assert_error(response, 401, "INVALID_ACTING_USER")

    def test_invalid_x_user_id_not_found(self, client):
        response = client.post(
            "/api/tickets",
            headers=acting_user_header(99999),
            json={"title": "T", "description": "D", "priority": "Low"},
        )
        assert_error(response, 401, "ACTING_USER_NOT_FOUND")

    def test_blank_title_rejected(self, client, alice):
        response = client.post(
            "/api/tickets",
            headers=acting_user_header(alice.id),
            json={"title": "   ", "description": "Valid description", "priority": "Low"},
        )
        assert_error(response, 422, "VALIDATION_ERROR")

    def test_blank_description_rejected(self, client, alice):
        response = client.post(
            "/api/tickets",
            headers=acting_user_header(alice.id),
            json={"title": "Valid title", "description": "  ", "priority": "Low"},
        )
        assert_error(response, 422, "VALIDATION_ERROR")

    def test_invalid_priority_rejected(self, client, alice):
        response = client.post(
            "/api/tickets",
            headers=acting_user_header(alice.id),
            json={"title": "T", "description": "D", "priority": "Urgent"},
        )
        assert_error(response, 422, "VALIDATION_ERROR")

    def test_invalid_assignee_rejected(self, client, alice):
        response = client.post(
            "/api/tickets",
            headers=acting_user_header(alice.id),
            json={"title": "T", "description": "D", "priority": "Low", "assignedTo": 99999},
        )
        assert_error(response, 422, "VALIDATION_ERROR")

    def test_created_ticket_is_persisted(self, client, alice, db_session):
        from app.models.ticket import Ticket

        created = create_ticket_via_api(client, alice.id, title="Persisted ticket")
        listed = client.get("/api/tickets").json()["items"]
        assert any(t["id"] == created["id"] for t in listed)
        db_ticket = db_session.get(Ticket, created["id"])
        assert db_ticket is not None
        assert db_ticket.title == "Persisted ticket"
