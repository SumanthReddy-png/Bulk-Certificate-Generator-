def test_create_job_returns_202(client):
    payload = {
        "event_name": "Python Summit",
        "recipients": [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob", "email": "bob@example.com"},
        ],
    }
    resp = client.post("/jobs", json=payload)
    assert resp.status_code == 202
    data = resp.json()
    assert "job_id" in data
    assert data["total"] == 2
    assert data["pending"] == 2
    assert data["failed"] == 0


def test_empty_recipients_returns_422(client):
    payload = {"event_name": "Summit", "recipients": []}
    resp = client.post("/jobs", json=payload)
    assert resp.status_code == 422


def test_too_many_recipients_returns_422(client, monkeypatch):
    import app.config as config_module
    monkeypatch.setattr(config_module, "MAX_RECIPIENTS", 3)

    payload = {
        "event_name": "Summit",
        "recipients": [{"name": f"User{i}", "email": f"user{i}@example.com"} for i in range(5)],
    }
    resp = client.post("/jobs", json=payload)
    assert resp.status_code == 422
