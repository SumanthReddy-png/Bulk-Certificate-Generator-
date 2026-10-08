from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfgen import canvas


def generate_certificate(
    cert_id: str,
    job_id: str,
    name: str,
    event_name: str,
    issue_date: str,
    issuer: str,
    storage_dir: str,
) -> str:
    job_dir = Path(storage_dir) / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    file_path = job_dir / f"{cert_id}.pdf"

    page_width, page_height = landscape(A4)
    c = canvas.Canvas(str(file_path), pagesize=landscape(A4))

    margin = 1.5 * cm
    c.setStrokeColor(colors.HexColor("#1a3c5e"))
    c.setLineWidth(3)
    c.rect(margin, margin, page_width - 2 * margin, page_height - 2 * margin)

    inner = 0.4 * cm
    c.setLineWidth(1)
    c.rect(
        margin + inner,
        margin + inner,
        page_width - 2 * margin - 2 * inner,
        page_height - 2 * margin - 2 * inner,
    )

    center_x = page_width / 2

    c.setFont("Times-Bold", 36)
    c.setFillColor(colors.HexColor("#1a3c5e"))
    c.drawCentredString(center_x, page_height - 4.5 * cm, "Certificate of Achievement")

    c.setStrokeColor(colors.HexColor("#c9a84c"))
    c.setLineWidth(1.5)
    c.line(
        page_width * 0.2,
        page_height - 5.2 * cm,
        page_width * 0.8,
        page_height - 5.2 * cm,
    )

    c.setFont("Times-Italic", 18)
    c.setFillColor(colors.HexColor("#333333"))
    c.drawCentredString(center_x, page_height - 7 * cm, "This certificate is proudly presented to")

    c.setFont("Times-Bold", 28)
    c.setFillColor(colors.HexColor("#1a3c5e"))
    c.drawCentredString(center_x, page_height - 9 * cm, name)

    c.setStrokeColor(colors.HexColor("#c9a84c"))
    c.setLineWidth(1)
    c.line(
        page_width * 0.25,
        page_height - 9.6 * cm,
        page_width * 0.75,
        page_height - 9.6 * cm,
    )

    c.setFont("Times-Roman", 16)
    c.setFillColor(colors.HexColor("#333333"))
    c.drawCentredString(center_x, page_height - 11 * cm, "for participation in")

    c.setFont("Times-Bold", 20)
    c.setFillColor(colors.HexColor("#1a3c5e"))
    c.drawCentredString(center_x, page_height - 12.2 * cm, event_name)

    c.setFont("Times-Roman", 14)
    c.setFillColor(colors.HexColor("#555555"))
    c.drawCentredString(center_x, page_height - 13.8 * cm, f"Date: {issue_date}")

    if issuer:
        c.setFont("Times-Italic", 14)
        c.setFillColor(colors.HexColor("#555555"))
        c.drawCentredString(center_x, page_height - 15 * cm, f"Issued by: {issuer}")

    c.save()
    return str(file_path)
