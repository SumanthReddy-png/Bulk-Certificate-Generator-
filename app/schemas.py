from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date


class RecipientIn(BaseModel):
    name: str
    email: str


class JobIn(BaseModel):
    event_name: str
    issue_date: Optional[date] = None
    issuer: Optional[str] = ""
    recipients: list[RecipientIn]

    @field_validator("recipients")
    @classmethod
    def check_recipient_count(cls, v):
        from app.config import MAX_RECIPIENTS
        if len(v) < 1:
            raise ValueError("At least one recipient is required")
        if len(v) > MAX_RECIPIENTS:
            raise ValueError(f"No more than {MAX_RECIPIENTS} recipients allowed")
        return v


class CertificateOut(BaseModel):
    id: str
    name: str
    email: str
    status: str
    error: Optional[str] = None
    download_url: Optional[str] = None


class JobCreatedOut(BaseModel):
    job_id: str
    status: str
    total: int
    pending: int
    failed: int


class JobStatusOut(BaseModel):
    job_id: str
    status: str
    total: int
    succeeded: int
    failed: int
    pending: int
    certificates: list[CertificateOut]
