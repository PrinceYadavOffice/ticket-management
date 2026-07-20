"""User API tests."""


def test_list_seeded_users(client, seeded_users):
    response = client.get("/api/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(seeded_users)
    emails = {user["email"] for user in data}
    assert emails == {u.email for u in seeded_users}


def test_list_users_returns_required_fields(client):
    response = client.get("/api/users")
    user = response.json()[0]
    assert set(user.keys()) == {"id", "name", "email", "role"}
