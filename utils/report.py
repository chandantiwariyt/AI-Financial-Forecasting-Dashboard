from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_report(ticker, summary):
    file_path = "stock_report.pdf"

    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph(f"Stock Report: {ticker}", styles['Title']))
    content.append(Spacer(1, 12))

    content.append(Paragraph(summary, styles['BodyText']))

    doc.build(content)

    return file_path