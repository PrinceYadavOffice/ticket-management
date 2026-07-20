"""Shared pytest fixtures — isolated file-based SQLite test database per test."""

import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1] / "src" / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app
from app.models import User


@pytest.fixture
def test_db_path(tmp_path):
    """Separate SQLite file per test — never touches data/tickets.db."""
    return tmp_path / "pytest_tickets.db"


@pytest.fixture
def db_engine(test_db_path):
    engine = create_engine(
        f"sqlite:///{test_db_path}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def seeded_users(db_session):
    users = [
        User(name="Alice Chen", email="alice@test.example", role="Agent"),
        User(name="Bob Martinez", email="bob@test.example", role="Admin"),
        User(name="Carol Okonkwo", email="carol@test.example", role="Agent"),
    ]
    db_session.add_all(users)
    db_session.commit()
    for user in users:
        db_session.refresh(user)
    return users


@pytest.fixture
def client(db_session, seeded_users):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def alice(seeded_users):
    return seeded_users[0]


@pytest.fixture
def bob(seeded_users):
    return seeded_users[1]


@pytest.fixture
def carol(seeded_users):
    return seeded_users[2]


@pytest.fixture
def sample_ticket(db_session, alice, bob):
    from tests.helpers import add_ticket_row

    return add_ticket_row(
        db_session,
        title="Test ticket",
        description="Test description",
        priority="High",
        status="Open",
        created_by_user_id=alice.id,
        assigned_to_user_id=bob.id,
    )
