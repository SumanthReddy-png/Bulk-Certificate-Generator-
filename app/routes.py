import io
import zipfile
from pathlib import Path
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.models import Job, Certificate
from app.schemas import JobIn, JobCreatedOut, JobStatusOut, CertificateOut
from app.service import create_job, process_job

router = APIRouter()


def get_session_factory():
    return SessionLocal


@router.post("/jobs", status_code=202, response_model=JobCreatedOut)
def submit_job(
    body: JobIn,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    session_factory=Depends(get_session_factory),
):
    job = create_job(body, db)
    background_tasks.add_task(process_job, job.id, session_factory)

    certs = db.query(Certificate).filter(Certificate.job_id == job.id).all()
    failed = sum(1 for c in certs if c.status == "failed")
    pending = sum(1 for c in certs if c.status == "pending")

    return JobCreatedOut(
        job_id=job.id,
        status=job.status,
        total=len(certs),
        pending=pending,
        failed=failed,
    )


@router.get("/jobs/{job_id}", response_model=JobStatusOut)
def get_job(job_id: str, request: Request, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    certs = db.query(Certificate).filter(Certificate.job_id == job_id).all()
    succeeded = sum(1 for c in certs if c.status == "success")
    failed = sum(1 for c in certs if c.status == "failed")
    pending = sum(1 for c in certs if c.status == "pending")

    cert_out = []
    for c in certs:
        download_url = None
        if c.status == "success":
            download_url = str(request.url_for("download_certificate", job_id=job_id, certificate_id=c.id))
        cert_out.append(
            CertificateOut(
                id=c.id,
                name=c.name,
                email=c.email,
                status=c.status,
                error=c.error,
                download_url=download_url,
            )
        )

    return JobStatusOut(
        job_id=job.id,
        status=job.status,
        total=len(certs),
        succeeded=succeeded,
        failed=failed,
        pending=pending,
        certificates=cert_out,
    )


@router.get("/jobs/{job_id}/certificates/{certificate_id}", name="download_certificate")
def download_certificate(job_id: str, certificate_id: str, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    cert = db.get(Certificate, certificate_id)
    if not cert or cert.job_id != job_id:
        raise HTTPException(status_code=404, detail="Certificate not found")

    if cert.status != "success":
        raise HTTPException(status_code=409, detail="Certificate is not available")

    return FileResponse(
        path=cert.file_path,
        media_type="application/pdf",
        filename=f"{cert.id}.pdf",
    )


@router.get("/jobs/{job_id}/download")
def download_zip(job_id: str, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    certs = db.query(Certificate).filter(
        Certificate.job_id == job_id,
        Certificate.status == "success",
    ).all()

    if not certs:
        raise HTTPException(status_code=409, detail="No successful certificates for this job")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for cert in certs:
            pdf_bytes = Path(cert.file_path).read_bytes()
            zf.writestr(f"{cert.name}_{cert.id}.pdf", pdf_bytes)

    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=job_{job_id}.zip"},
    )
