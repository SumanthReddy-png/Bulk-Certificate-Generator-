import zipfile
import io


def test_single_pdf_download(client):
    payload = {
        "event_name": "Retrieval Test",
        "recipients": [{"name": "Eve", "email": "eve@example.com"}],
    }
    resp = client.post("/jobs", json=payload)
    job_id = resp.json()["job_id"]

    status = client.get(f"/jobs/{job_id}").json()
    cert = next(c for c in status["certificates"] if c["status"] == "success")

    pdf_resp = client.get(f"/jobs/{job_id}/certificates/{cert['id']}")
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert pdf_resp.content[:4] == b"%PDF"


def test_zip_contains_only_successful(client):
    payload = {
        "event_name": "Zip Test",
        "recipients": [
            {"name": "Frank", "email": "frank@example.com"},
            {"name": "Grace", "email": "grace@example.com"},
            {"name": "Bad", "email": "not-an-email"},
        ],
    }
    resp = client.post("/jobs", json=payload)
    job_id = resp.json()["job_id"]

    zip_resp = client.get(f"/jobs/{job_id}/download")
    assert zip_resp.status_code == 200
    assert "application/zip" in zip_resp.headers["content-type"]

    zf = zipfile.ZipFile(io.BytesIO(zip_resp.content))
    assert len(zf.namelist()) == 2


def test_409_for_failed_certificate(client):
    payload = {
        "event_name": "409 Test",
        "recipients": [{"name": "Bad", "email": "bad-email"}],
    }
    resp = client.post("/jobs", json=payload)
    job_id = resp.json()["job_id"]

    status = client.get(f"/jobs/{job_id}").json()
    cert = status["certificates"][0]
    assert cert["status"] == "failed"

    pdf_resp = client.get(f"/jobs/{job_id}/certificates/{cert['id']}")
    assert pdf_resp.status_code == 409


def test_404_unknown_job_certificate(client):
    resp = client.get("/jobs/no-such-job/certificates/no-such-cert")
    assert resp.status_code == 404


def test_404_unknown_job_download(client):
    resp = client.get("/jobs/no-such-job/download")
    assert resp.status_code == 404
