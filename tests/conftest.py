"""Shared pytest fixtures."""

import sys
from pathlib import Path

# Ensure src/backend is on PYTHONPATH when running tests from repo root
_BACKEND = Path(__file__).resolve().parents[1] / "src" / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models import Comment, Ticket, User


@pytest.fixture
def db_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


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
    for u in users:
        db_session.refresh(u)
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
def sample_ticket(db_session, alice, bob):
    from datetime import datetime, timezone

    ticket = Ticket(
        title="Test ticket",
        description="Test description",
        priority="High",
        status="Open",
        assigned_to_user_id=bob.id,
        created_by_user_id=alice.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)
    return ticket
