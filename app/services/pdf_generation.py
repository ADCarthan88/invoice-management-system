from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO
from app.models.invoice import Invoice
from app.models.client import Client

def generate_invoice_pdf(invoice: Invoice, client: Client) -> BytesIO:
    """Generate a PDF for the given invoice."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("Invoice", styles['Title']))
    story.append(Spacer(1, 12))

    # Invoice details
    story.append(Paragraph(f"Invoice ID: {invoice.id}", styles['Normal']))
    story.append(Paragraph(f"Date: {invoice.created_at.strftime('%Y-%m-%d')}", styles['Normal']))
    story.append(Paragraph(f"Due Date: {invoice.due_date.strftime('%Y-%m-%d')}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Client details
    story.append(Paragraph("Bill To:", styles['Heading2']))
    story.append(Paragraph(client.name, styles['Normal']))
    story.append(Paragraph(client.email, styles['Normal']))
    if client.address:
        story.append(Paragraph(client.address, styles['Normal']))
    story.append(Spacer(1, 12))

    # Invoice items (assuming simple, can be extended)
    data = [['Description', 'Amount']]
    data.append([invoice.description or 'Invoice', f"${invoice.amount:.2f}"])
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]))
    story.append(table)
    story.append(Spacer(1, 12))

    # Total
    story.append(Paragraph(f"Total: ${invoice.amount:.2f}", styles['Heading3']))

    doc.build(story)
    buffer.seek(0)
    return buffer