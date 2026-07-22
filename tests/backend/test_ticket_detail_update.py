"""Ticket detail and update API tests."""

from tests.helpers import acting_user_header, assert_error


class TestTicketDetailAndUpdate:
    def test_details_include_comments(self, client, sample_ticket, alice, bob):
        client.post(
            f"/api/tickets/{sample_ticket.id}/comments",
            headers=acting_user_header(bob.id),
            json={"message": "On it"},
        )
        response = client.get(f"/api/tickets/{sample_ticket.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["comments"]) == 1
        assert data["comments"][0]["message"] == "On it"
        assert data["comments"][0]["createdBy"]["id"] == bob.id
        assert data["creator"]["id"] == alice.id

    def test_nonexistent_ticket_returns_404(self, client):
        response = client.get("/api/tickets/99999")
        assert_error(response, 404, "NOT_FOUND")

    def test_valid_field_updates_succeed(self, client, sample_ticket):
        response = client.patch(
            f"/api/tickets/{sample_ticket.id}",
            json={
                "title": "Updated title",
                "description": "Updated description",
                "priority": "Critical",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated title"
        assert data["description"] == "Updated description"
        assert data["priority"] == "Critical"

    def test_status_cannot_change_via_general_update(self, client, sample_ticket, db_session):
        response = client.patch(
            f"/api/tickets/{sample_ticket.id}",
            json={"status": "Closed"},
        )
        assert_error(response, 422, "VALIDATION_ERROR")
        ticket = db_session.get(type(sample_ticket), sample_ticket.id)
        assert ticket.status == "Open"

    def test_nonexistent_assignee_rejected(self, client, sample_ticket):
        response = client.patch(
            f"/api/tickets/{sample_ticket.id}",
            json={"assignedTo": 99999},
        )
        assert_error(response, 422, "VALIDATION_ERROR")

    def test_unassign_via_null(self, client, sample_ticket, bob):
        response = client.patch(
            f"/api/tickets/{sample_ticket.id}",
            json={"assignedTo": None},
        )
        assert response.status_code == 200
        assert response.json()["assignedTo"] is None

    def test_blank_title_on_patch_returns_422(self, client, sample_ticket):
        response = client.patch(
            f"/api/tickets/{sample_ticket.id}",
            json={"title": "   "},
        )
        assert_error(response, 422, "VALIDATION_ERROR")

    def test_invalid_priority_on_patch_returns_422(self, client, sample_ticket):
        response = client.patch(
            f"/api/tickets/{sample_ticket.id}",
            json={"priority": "Urgent"},
        )
        assert_error(response, 422, "VALIDATION_ERROR")

    def test_malformed_json_on_patch_returns_422(self, client, sample_ticket):
        response = client.patch(
            f"/api/tickets/{sample_ticket.id}",
            content="{bad",
            headers={"Content-Type": "application/json"},
        )
        assert_error(response, 422, "VALIDATION_ERROR")
