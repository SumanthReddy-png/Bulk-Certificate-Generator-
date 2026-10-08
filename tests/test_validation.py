def test_invalid_email_marked_failed(client):
    payload = {
        "event_name": "Test Event",
        "recipients": [
            {"name": "Valid User", "email": "valid@example.com"},
            {"name": "Bad Email", "email": "not-an-email"},
        ],
    }
    resp = client.post("/jobs", json=payload)
    assert resp.status_code == 202
    data = resp.json()
    assert data["failed"] == 1
    assert data["pending"] == 1


def test_empty_name_marked_failed(client):
    payload = {
        "event_name": "Test Event",
        "recipients": [
            {"name": "", "email": "empty@example.com"},
            {"name": "Fine", "email": "fine@example.com"},
        ],
    }
    resp = client.post("/jobs", json=payload)
    assert resp.status_code == 202
    data = resp.json()
    assert data["failed"] == 1
    assert data["pending"] == 1


def test_overlong_name_marked_failed(client):
    payload = {
        "event_name": "Test Event",
        "recipients": [
            {"name": "A" * 101, "email": "long@example.com"},
            {"name": "Short", "email": "short@example.com"},
        ],
    }
    resp = client.post("/jobs", json=payload)
    assert resp.status_code == 202
    data = resp.json()
    assert data["failed"] == 1
    assert data["pending"] == 1


def test_duplicate_email_marked_failed(client):
    payload = {
        "event_name": "Test Event",
        "recipients": [
            {"name": "First", "email": "dup@example.com"},
            {"name": "Second", "email": "dup@example.com"},
        ],
    }
    resp = client.post("/jobs", json=payload)
    assert resp.status_code == 202
    data = resp.json()
    assert data["failed"] == 1
    assert data["pending"] == 1
