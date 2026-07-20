"""Ticket list, search, filter, and pagination tests."""

from tests.helpers import add_ticket_row, create_ticket_via_api


class TestTicketList:
    def test_returns_persisted_tickets(self, client, alice):
        create_ticket_via_api(client, alice.id, title="Persisted A")
        create_ticket_via_api(client, alice.id, title="Persisted B")
        response = client.get("/api/tickets")
        assert response.status_code == 200
        titles = {t["title"] for t in response.json()["items"]}
        assert "Persisted A" in titles
        assert "Persisted B" in titles

    def test_search_by_title(self, client, db_session, alice):
        add_ticket_row(
            db_session,
            title="UniqueAlphaTitle",
            description="generic",
            created_by_user_id=alice.id,
        )
        add_ticket_row(
            db_session,
            title="Other",
            description="generic",
            created_by_user_id=alice.id,
        )
        response = client.get("/api/tickets?q=UniqueAlpha")
        titles = [t["title"] for t in response.json()["items"]]
        assert titles == ["UniqueAlphaTitle"]

    def test_search_by_description(self, client, db_session, alice):
        add_ticket_row(
            db_session,
            title="Title",
            description="Contains BetaKeyword here",
            created_by_user_id=alice.id,
        )
        add_ticket_row(
            db_session,
            title="Title2",
            description="nothing special",
            created_by_user_id=alice.id,
        )
        response = client.get("/api/tickets?q=BetaKeyword")
        assert len(response.json()["items"]) == 1
        assert "BetaKeyword" in response.json()["items"][0]["description"]

    def test_filter_by_status(self, client, db_session, alice):
        add_ticket_row(
            db_session,
            title="Open ticket",
            description="d",
            status="Open",
            created_by_user_id=alice.id,
        )
        add_ticket_row(
            db_session,
            title="Closed ticket",
            description="d",
            status="Closed",
            created_by_user_id=alice.id,
        )
        response = client.get("/api/tickets?status=Open")
        assert all(t["status"] == "Open" for t in response.json()["items"])
        assert any(t["title"] == "Open ticket" for t in response.json()["items"])

    def test_filter_by_priority(self, client, db_session, alice):
        add_ticket_row(
            db_session,
            title="Critical issue",
            description="d",
            priority="Critical",
            created_by_user_id=alice.id,
        )
        add_ticket_row(
            db_session,
            title="Low issue",
            description="d",
            priority="Low",
            created_by_user_id=alice.id,
        )
        response = client.get("/api/tickets?priority=Critical")
        items = response.json()["items"]
        assert len(items) == 1
        assert items[0]["priority"] == "Critical"

    def test_filter_by_assignee(self, client, db_session, alice, bob):
        add_ticket_row(
            db_session,
            title="Assigned to Bob",
            description="d",
            created_by_user_id=alice.id,
            assigned_to_user_id=bob.id,
        )
        add_ticket_row(
            db_session,
            title="Unassigned",
            description="d",
            created_by_user_id=alice.id,
            assigned_to_user_id=None,
        )
        response = client.get(f"/api/tickets?assignedTo={bob.id}")
        items = response.json()["items"]
        assert len(items) == 1
        assert items[0]["assignedTo"] == bob.id

    def test_filter_by_creator(self, client, db_session, alice, bob):
        add_ticket_row(
            db_session,
            title="Alice ticket",
            description="d",
            created_by_user_id=alice.id,
        )
        add_ticket_row(
            db_session,
            title="Bob ticket",
            description="d",
            created_by_user_id=bob.id,
        )
        response = client.get(f"/api/tickets?createdBy={bob.id}")
        items = response.json()["items"]
        assert len(items) == 1
        assert items[0]["createdBy"] == bob.id

    def test_pagination(self, client, db_session, alice):
        for i in range(5):
            add_ticket_row(
                db_session,
                title=f"Page ticket {i}",
                description="d",
                created_by_user_id=alice.id,
            )
        page1 = client.get("/api/tickets?page=1&pageSize=2").json()
        page2 = client.get("/api/tickets?page=2&pageSize=2").json()
        assert page1["total"] == 5
        assert len(page1["items"]) == 2
        assert page1["page"] == 1
        assert page1["pageSize"] == 2
        assert len(page2["items"]) == 2
        assert page2["page"] == 2
        page1_ids = {t["id"] for t in page1["items"]}
        page2_ids = {t["id"] for t in page2["items"]}
        assert page1_ids.isdisjoint(page2_ids)
