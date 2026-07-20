"""Comment API tests."""

from tests.helpers import acting_user_header, assert_error


class TestComments:
    def test_valid_comment_creation(self, client, sample_ticket, bob):
        response = client.post(
            f"/api/tickets/{sample_ticket.id}/comments",
            headers=acting_user_header(bob.id),
            json={"message": "Investigating now"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Investigating now"
        assert data["ticketId"] == sample_ticket.id
        assert data["createdBy"]["id"] == bob.id
        assert "createdAt" in data

    def test_blank_comment_rejected(self, client, sample_ticket, bob):
        response = client.post(
            f"/api/tickets/{sample_ticket.id}/comments",
            headers=acting_user_header(bob.id),
            json={"message": "   "},
        )
        assert_error(response, 422, "VALIDATION_ERROR")

    def test_missing_ticket_returns_404(self, client, bob):
        response = client.post(
            "/api/tickets/99999/comments",
            headers=acting_user_header(bob.id),
            json={"message": "Hello"},
        )
        assert_error(response, 404, "NOT_FOUND")

    def test_invalid_user_rejected(self, client, sample_ticket):
        response = client.post(
            f"/api/tickets/{sample_ticket.id}/comments",
            headers=acting_user_header(99999),
            json={"message": "Hello"},
        )
        assert_error(response, 401, "ACTING_USER_NOT_FOUND")

    def test_comment_persistence(self, client, sample_ticket, bob):
        create = client.post(
            f"/api/tickets/{sample_ticket.id}/comments",
            headers=acting_user_header(bob.id),
            json={"message": "Persisted comment"},
        )
        assert create.status_code == 201
        detail = client.get(f"/api/tickets/{sample_ticket.id}").json()
        assert any(c["message"] == "Persisted comment" for c in detail["comments"])

    def test_comments_ordered_chronologically(self, client, sample_ticket, alice, bob):
        client.post(
            f"/api/tickets/{sample_ticket.id}/comments",
            headers=acting_user_header(alice.id),
            json={"message": "First"},
        )
        client.post(
            f"/api/tickets/{sample_ticket.id}/comments",
            headers=acting_user_header(bob.id),
            json={"message": "Second"},
        )
        client.post(
            f"/api/tickets/{sample_ticket.id}/comments",
            headers=acting_user_header(alice.id),
            json={"message": "Third"},
        )
        messages = [
            c["message"]
            for c in client.get(f"/api/tickets/{sample_ticket.id}").json()["comments"]
        ]
        assert messages == ["First", "Second", "Third"]
