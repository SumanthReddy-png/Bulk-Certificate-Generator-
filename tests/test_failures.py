import app.service as service_module


def test_one_failure_isolated(client, monkeypatch):
    target_email = "boom@example.com"

    original_generate = service_module.generate_certificate

    def patched_generate(cert_id, job_id, name, event_name, issue_date, issuer, storage_dir):
        if name == "Boom":
            raise RuntimeError("Simulated generation failure")
        return original_generate(
            cert_id=cert_id,
            job_id=job_id,
            name=name,
            event_name=event_name,
            issue_date=issue_date,
            issuer=issuer,
            storage_dir=storage_dir,
        )

    monkeypatch.setattr(service_module, "generate_certificate", patched_generate)

    payload = {
        "event_name": "Failure Test",
        "recipients": [
            {"name": "Boom", "email": target_email},
            {"name": "Alice", "email": "alice2@example.com"},
            {"name": "Bob", "email": "bob2@example.com"},
        ],
    }
    resp = client.post("/jobs", json=payload)
    assert resp.status_code == 202
    job_id = resp.json()["job_id"]

    status_resp = client.get(f"/jobs/{job_id}")
    data = status_resp.json()

    assert data["status"] == "completed_with_errors"
    assert data["succeeded"] == 2
    assert data["failed"] == 1

    failed_certs = [c for c in data["certificates"] if c["status"] == "failed"]
    assert len(failed_certs) == 1
    assert failed_certs[0]["email"] == target_email
    assert "Simulated generation failure" in failed_certs[0]["error"]
