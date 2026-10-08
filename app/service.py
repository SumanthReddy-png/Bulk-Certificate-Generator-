import uuid
from datetime import date
from typing import Callable
from sqlalchemy.orm import Session
from app.models import Job, Certificate
from app.schemas import JobIn
from app.validation import validate_recipient
from app.generator import generate_certificate
from app.database import SessionLocal
from app.config import STORAGE_DIR


def create_job(data: JobIn, db: Session) -> Job:
    issue_date = str(data.issue_date or date.today())
    issuer = data.issuer or ""

    job = Job(
        id=str(uuid.uuid4()),
        event_name=data.event_name,
        issue_date=issue_date,
        issuer=issuer,
        status="pending",
    )
    db.add(job)

    seen_emails: set[str] = set()
    for r in data.recipients:
        cert_id = str(uuid.uuid4())
        error = validate_recipient(r.name, r.email)
        if error is None and r.email in seen_emails:
            error = "Duplicate email in this request"
        if r.email:
            seen_emails.add(r.email)

        cert = Certificate(
            id=cert_id,
            job_id=job.id,
            name=r.name,
            email=r.email,
            status="failed" if error else "pending",
            error=error,
        )
        db.add(cert)

    db.commit()
    db.refresh(job)
    return job


def process_job(job_id: str, session_factory: Callable = None) -> None:
    factory = session_factory if session_factory is not None else SessionLocal
    db = factory()
    try:
        job = db.get(Job, job_id)
        if not job:
            return

        job.status = "processing"
        db.commit()

        certs = db.query(Certificate).filter(
            Certificate.job_id == job_id,
            Certificate.status == "pending",
        ).all()

        for cert in certs:
            try:
                path = generate_certificate(
                    cert_id=cert.id,
                    job_id=job_id,
                    name=cert.name,
                    event_name=job.event_name,
                    issue_date=job.issue_date,
                    issuer=job.issuer,
                    storage_dir=STORAGE_DIR,
                )
                cert.status = "success"
                cert.file_path = path
            except Exception as exc:
                cert.status = "failed"
                cert.error = str(exc)
            db.commit()

        failed_count = db.query(Certificate).filter(
            Certificate.job_id == job_id,
            Certificate.status == "failed",
        ).count()

        job.status = "completed_with_errors" if failed_count > 0 else "completed"
        db.commit()
    finally:
        db.close()
