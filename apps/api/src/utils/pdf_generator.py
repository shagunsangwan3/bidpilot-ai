from io import BytesIO

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate


def create_proposal_pdf(title: str, content: str):
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("<b>BidPilot AI</b>", styles["Title"]))
    elements.append(Paragraph(title, styles["Heading2"]))
    elements.append(Paragraph("<br/>", styles["Normal"]))

    for line in content.split("\n"):
        if line.strip():
            elements.append(
                Paragraph(line, styles["BodyText"])
            )

    doc.build(elements)

    buffer.seek(0)

    return buffer