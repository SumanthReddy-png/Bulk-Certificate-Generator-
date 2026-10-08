# Certificate Generator

## Overview

- Accepts a list of recipients via a REST API and generates a personalized PDF certificate for each one.
- Built with FastAPI, SQLAlchemy (SQLite), and ReportLab. No external task queue required.
- Certificate generation runs in the background via FastAPI `BackgroundTasks`. The API returns immediately with a job ID; the client polls for status.

---

## Project Structure

```
certificate-generator/
  app/
    __init__.py
    main.py          # app setup, lifespan, router
    config.py        # env-based settings
    database.py      # engine, session, Base, get_db
    models.py        # Job and Certificate tables
    schemas.py       # Pydantic request/response models
    validation.py    # per-recipient validation
    generator.py     # ReportLab PDF rendering
    service.py       # create_job, process_job
    routes.py        # four API endpoints
  tests/
    conftest.py
    test_jobs.py
    test_validation.py
    test_generator.py
    test_status.py
    test_failures.py
    test_retrieval.py
  requirements.txt
  README.md
```

---

## Setup

```bash
python -m venv venv
```

Activate:

- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Run the App

```bash
uvicorn app.main:app --reload
```

Interactive docs: http://127.0.0.1:8000/docs

---

## Run Tests

```bash
pytest -v
```

---

## API Endpoints

| Method | Path                                          | Purpose                                  |
|--------|-----------------------------------------------|------------------------------------------|
| POST   | `/jobs`                                       | Submit a generation job                  |
| GET    | `/jobs/{job_id}`                              | Check job status and certificate list    |
| GET    | `/jobs/{job_id}/certificates/{cert_id}`       | Download a single PDF                    |
| GET    | `/jobs/{job_id}/download`                     | Download all successful PDFs as a ZIP    |

---

## Submit a Request

```bash
curl -X POST http://127.0.0.1:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "event_name": "Python Summit 2026",
    "issue_date": "2026-10-08",
    "issuer": "Tech Academy",
    "recipients": [
      { "name": "Alice Smith", "email": "alice@example.com" },
      { "name": "Bob Jones",   "email": "bob@example.com" },
      { "name": "Bad Entry",   "email": "not-an-email" }
    ]
  }'
```

Sample 202 response:

```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "pending",
  "total": 3,
  "pending": 2,
  "failed": 1
}
```

---

## Check Status

```bash
curl http://127.0.0.1:8000/jobs/3fa85f64-5717-4562-b3fc-2c963f66afa6
```

Sample response:

```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "completed_with_errors",
  "total": 3,
  "succeeded": 2,
  "failed": 1,
  "pending": 0,
  "certificates": [
    {
      "id": "a1b2c3d4-1111-2222-3333-444455556666",
      "name": "Alice Smith",
      "email": "alice@example.com",
      "status": "success",
      "error": null,
      "download_url": "http://127.0.0.1:8000/jobs/3fa85f64-.../certificates/a1b2c3d4-..."
    },
    {
      "id": "b2c3d4e5-1111-2222-3333-444455556666",
      "name": "Bob Jones",
      "email": "bob@example.com",
      "status": "success",
      "error": null,
      "download_url": "http://127.0.0.1:8000/jobs/3fa85f64-.../certificates/b2c3d4e5-..."
    },
    {
      "id": "c3d4e5f6-1111-2222-3333-444455556666",
      "name": "Bad Entry",
      "email": "not-an-email",
      "status": "failed",
      "error": "Invalid email address",
      "download_url": null
    }
  ]
}
```

Possible `status` values: `pending`, `processing`, `completed`, `completed_with_errors`.

---

## Download Certificates

Single PDF:

```bash
curl -o alice.pdf \
  http://127.0.0.1:8000/jobs/3fa85f64-5717-4562-b3fc-2c963f66afa6/certificates/a1b2c3d4-1111-2222-3333-444455556666
```

All successful certificates as a ZIP:

```bash
curl -o job.zip \
  http://127.0.0.1:8000/jobs/3fa85f64-5717-4562-b3fc-2c963f66afa6/download
```

- Returns `409` if the certificate failed or the job has no successful certificates.
- Returns `404` for unknown job or certificate IDs.

---

## Design Decisions

- **202 Accepted with background processing** — PDF generation time scales with recipient count. Returning immediately and letting the client poll avoids long-held HTTP connections and timeouts.
- **Per-certificate error isolation** — each certificate is generated inside its own `try/except`. One bad recipient cannot abort the rest of the batch.
- **Invalid recipients stored as failed, not rejected** — the whole request is not thrown away because of one bad email or name. Valid recipients are still processed; the caller can see exactly which rows failed and why.
- **SQLite with SQLAlchemy** — zero configuration, appropriate for development and small deployments. To switch to Postgres, set the `DATABASE_URL` environment variable to a `postgresql://` connection string; nothing else changes.
- **ReportLab for PDF generation** — pure-Python, no system dependencies, straightforward canvas API for drawing text, borders, and layout on a landscape A4 page.

---

## Limitations

- `BackgroundTasks` runs inside the web server process. If the server restarts while a job is processing, that job stalls in the `processing` state and its remaining certificates are never generated.
- For production, replace `BackgroundTasks` with a proper task queue such as Celery or RQ backed by Redis or a database broker. Jobs would then survive restarts and scale across multiple workers.
- There is no authentication or authorization. All job and certificate data is publicly accessible to anyone with the job ID.
