import uuid
from pathlib import Path
from app.generator import generate_certificate


def test_generate_creates_pdf(tmp_path):
    cert_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())
    path = generate_certificate(
        cert_id=cert_id,
        job_id=job_id,
        name="Jane Doe",
        event_name="Tech Conference",
        issue_date="2026-10-08",
        issuer="Test Org",
        storage_dir=str(tmp_path),
    )
    file = Path(path)
    assert file.exists()
    assert file.stat().st_size > 0
    assert file.read_bytes()[:4] == b"%PDF"
