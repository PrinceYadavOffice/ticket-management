"""CSV export API tests."""

import csv
import io
from datetime import datetime, timezone

import pytest

from tests.helpers import acting_user_header, assert_error


class TestCsvExport:
    def test_includes_only_acting_users_tickets(self, client, alice, bob, db_session):
        from app.models.ticket import Ticket

        now = datetime.now(timezone.utc)
        db_session.add(
            Ticket(
                title="Alice export",
                description="d",
                priority="Low",
                status="Open",
                created_by_user_id=alice.id,
                created_at=now,
                updated_at=now,
            )
        )
        db_session.add(
            Ticket(
                title="Bob export",
                description="d",
                priority="Low",
                status="Open",
                created_by_user_id=bob.id,
                created_at=now,
                updated_at=now,
            )
        )
        db_session.commit()

        response = client.get(
            "/api/tickets/export.csv",
            headers=acting_user_header(alice.id),
        )
        assert response.status_code == 200
        assert "Alice export" in response.text
        assert "Bob export" not in response.text

    def test_escapes_commas_and_quotes(self, client, alice, db_session):
        from app.models.ticket import Ticket

        now = datetime.now(timezone.utc)
        db_session.add(
            Ticket(
                title='Issue with "quotes", and commas',
                description="Line one, line two",
                priority="Low",
                status="Open",
                created_by_user_id=alice.id,
                created_at=now,
                updated_at=now,
            )
        )
        db_session.commit()

        response = client.get(
            "/api/tickets/export.csv",
            headers=acting_user_header(alice.id),
        )
        rows = list(csv.reader(io.StringIO(response.text)))
        assert len(rows) == 2
        assert rows[1][1] == 'Issue with "quotes", and commas'
        assert rows[1][2] == "Line one, line two"

    def test_empty_results_header_only(self, client, bob):
        response = client.get(
            "/api/tickets/export.csv",
            headers=acting_user_header(bob.id),
        )
        assert response.status_code == 200
        lines = response.text.strip().splitlines()
        assert len(lines) == 1
        assert "commentCount" in lines[0]

    def test_rejects_invalid_user(self, client):
        response = client.get(
            "/api/tickets/export.csv",
            headers=acting_user_header(99999),
        )
        assert_error(response, 401, "ACTING_USER_NOT_FOUND")

    def test_response_headers(self, client, alice):
        response = client.get(
            "/api/tickets/export.csv",
            headers=acting_user_header(alice.id),
        )
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        assert "attachment" in response.headers["content-disposition"]
        assert f"my-tickets-{alice.id}-" in response.headers["content-disposition"]

    @pytest.mark.parametrize("prefix", ["=", "+", "-", "@"])
    def test_formula_injection_mitigation(self, client, alice, db_session, prefix):
        from app.models.ticket import Ticket

        now = datetime.now(timezone.utc)
        db_session.add(
            Ticket(
                title=f"{prefix}cmd|",
                description="safe",
                priority="Low",
                status="Open",
                created_by_user_id=alice.id,
                created_at=now,
                updated_at=now,
            )
        )
        db_session.commit()

        response = client.get(
            "/api/tickets/export.csv",
            headers=acting_user_header(alice.id),
        )
        rows = list(csv.reader(io.StringIO(response.text)))
        assert rows[1][1].startswith("'")
