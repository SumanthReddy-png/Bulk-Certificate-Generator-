from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)
    event_name = Column(String, nullable=False)
    issue_date = Column(String, nullable=False)
    issuer = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    certificates = relationship("Certificate", back_populates="job")


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(String, primary_key=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    error = Column(String, nullable=True)
    file_path = Column(String, nullable=True)

    job = relationship("Job", back_populates="certificates")
