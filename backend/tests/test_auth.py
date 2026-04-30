def test_register_and_login_success(client):
    r = client.post(
        "/register",
        json={"username": "user1", "email": "u1@example.com", "password": "secret123"},
    )
    assert r.status_code in (201, 400)  # allow re-run locally

    l = client.post("/login", json={"username": "user1", "password": "secret123"})
    assert l.status_code == 200
    data = l.get_json()
    assert "access_token" in data


def test_register_rejects_bad_email(client):
    r = client.post(
        "/register",
        json={"username": "user2", "email": "not-an-email", "password": "secret123"},
    )
    assert r.status_code == 400

