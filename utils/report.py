from pathlib import Path
import tempfile
from uuid import uuid4
from xml.sax.saxutils import escape

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def generate_report(ticker, summary):
    safe_ticker = "".join(ch for ch in str(ticker) if ch.isalnum() or ch in ("-", "_", ".")).strip(".")
    safe_ticker = safe_ticker or "stock"
    file_path = Path(tempfile.gettempdir()) / f"{safe_ticker}_report_{uuid4().hex}.pdf"

    doc = SimpleDocTemplate(str(file_path))
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph(f"Stock Report: {escape(str(ticker))}", styles["Title"]))
    content.append(Spacer(1, 12))

    for line in str(summary).splitlines():
        text = line.strip()
        if text:
            content.append(Paragraph(escape(text), styles["BodyText"]))
            content.append(Spacer(1, 6))

    doc.build(content)

    return str(file_path)
