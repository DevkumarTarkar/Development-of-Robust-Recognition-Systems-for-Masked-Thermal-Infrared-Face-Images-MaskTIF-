from datetime import datetime, timezone


def _get_token(client):
    client.post(
        "/register",
        json={"username": "hist1", "email": "h1@example.com", "password": "secret123"},
    )
    r = client.post("/login", json={"username": "hist1", "password": "secret123"})
    assert r.status_code == 200
    return r.get_json()["access_token"]


def test_predictions_requires_auth(client):
    r = client.get("/predictions")
    assert r.status_code in (401, 422)


def test_predictions_returns_items(client, app):
    token = _get_token(client)

    from database import db, User, Prediction

    with app.app_context():
        user = User.query.filter_by(username="hist1").first()
        assert user is not None

        p = Prediction(
            user_id=user.id,
            image_path="backend/uploads/sample.jpg",
            predicted_person="person_1",
            confidence=0.88,
            timestamp=datetime.now(timezone.utc),
        )
        db.session.add(p)
        db.session.commit()

    r = client.get("/predictions?limit=10", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.get_json()
    assert data["count"] >= 1
    assert isinstance(data["items"], list)
    assert data["items"][0]["predicted_person"]

