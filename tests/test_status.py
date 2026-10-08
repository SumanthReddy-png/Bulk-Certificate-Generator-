def test_status_correct_counts(client):
    payload = {
        "event_name": "Status Test",
        "recipients": [
            {"name": "Alice", "email": "a@example.com"},
            {"name": "Bob", "email": "b@example.com"},
            {"name": "Bad", "email": "not-valid"},
        ],
    }
    resp = client.post("/jobs", json=payload)
    assert resp.status_code == 202
    job_id = resp.json()["job_id"]

    status_resp = client.get(f"/jobs/{job_id}")
    assert status_resp.status_code == 200
    data = status_resp.json()
    assert data["total"] == 3
    assert data["succeeded"] == 2
    assert data["failed"] == 1
    assert data["pending"] == 0
    assert data["status"] == "completed_with_errors"


def test_status_completed_all_valid(client):
    payload = {
        "event_name": "Full Pass",
        "recipients": [
            {"name": "Carol", "email": "carol@example.com"},
            {"name": "Dave", "email": "dave@example.com"},
        ],
    }
    resp = client.post("/jobs", json=payload)
    job_id = resp.json()["job_id"]

    status_resp = client.get(f"/jobs/{job_id}")
    data = status_resp.json()
    assert data["status"] == "completed"
    assert data["succeeded"] == 2
    assert data["failed"] == 0


def test_status_404_unknown_job(client):
    resp = client.get("/jobs/does-not-exist-abc123")
    assert resp.status_code == 404
