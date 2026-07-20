"""User endpoint tests."""


def test_list_users(client, seeded_users):
    response = client.get("/api/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == "Alice Chen"
