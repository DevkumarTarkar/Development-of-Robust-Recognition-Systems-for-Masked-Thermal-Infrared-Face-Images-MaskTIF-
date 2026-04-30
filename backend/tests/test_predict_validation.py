import io


def _get_token(client):
    client.post(
        "/register",
        json={"username": "pred1", "email": "p1@example.com", "password": "secret123"},
    )
    r = client.post("/login", json={"username": "pred1", "password": "secret123"})
    assert r.status_code == 200
    return r.get_json()["access_token"]


def test_predict_requires_auth(client):
    r = client.post("/predict")
    assert r.status_code in (401, 422)


def test_predict_rejects_invalid_file_type(client):
    token = _get_token(client)
    data = {"image": (io.BytesIO(b"not an image"), "sample.txt")}
    r = client.post("/predict", headers={"Authorization": f"Bearer {token}"}, data=data)
    assert r.status_code == 400
    body = r.get_json()
    assert "message" in body

