"""CSV export tests."""


def test_export_csv_requires_acting_user(client):
    response = client.get("/api/tickets/export.csv")
    assert response.status_code == 401


def test_export_csv_only_creator_tickets(client, alice, bob, db_session):
    from datetime import datetime, timezone

    from app.models.ticket import Ticket

    db_session.add(
        Ticket(
            title="Alice ticket",
            description="By alice",
            priority="Low",
            status="Open",
            created_by_user_id=alice.id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )
    db_session.add(
        Ticket(
            title="Bob ticket",
            description="By bob",
            priority="Low",
            status="Open",
            created_by_user_id=bob.id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )
    db_session.commit()

    response = client.get("/api/tickets/export.csv", headers={"X-User-Id": str(alice.id)})
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "attachment" in response.headers["content-disposition"]
    body = response.text
    assert "Alice ticket" in body
    assert "Bob ticket" not in body


def test_export_csv_header_only(client, bob):
    response = client.get("/api/tickets/export.csv", headers={"X-User-Id": str(bob.id)})
    assert response.status_code == 200
    lines = response.text.strip().splitlines()
    assert len(lines) == 1
    assert "commentCount" in lines[0]


def test_export_csv_formula_injection_mitigation(client, alice, db_session):
    from datetime import datetime, timezone

    from app.models.ticket import Ticket

    db_session.add(
        Ticket(
            title="=1+1",
            description="Normal",
            priority="Low",
            status="Open",
            created_by_user_id=alice.id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )
    db_session.commit()

    response = client.get("/api/tickets/export.csv", headers={"X-User-Id": str(alice.id)})
    assert "'=1+1" in response.text or "'=1+1" in response.text
