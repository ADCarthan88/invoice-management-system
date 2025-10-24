import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.invoice import Invoice
from app.config import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD # Assuming config has these

def send_email(to_email: str, subject: str, body: str):
    """Send an email using SMTP."""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_overdue_reminders(db: Session):
    """Send reminders for overdue invoices."""
    overdue_invoices = db.query(Invoice).filter(
        Invoice.due_date < datetime.now(),
        Invoice.paid == False
    ).all()

    for invoice in overdue_invoices:
        client_email = invoice.client.email
        subject = f"Reminder: Invoice #{invoice.id} is overdue."
        body = (
            f"Dear {invoice.client.name},\n\n"
            f"This is a reminder that your invoice #{invoice.id} is overdue.\n"
            f"The due date was {invoice.due_date.strftime('%Y-%m-%d')}.\n"
            f"Please make the payment at your earliest convenience.\n\n"
            f"Thank you!"
        )

        if send_email(client_email, subject, body):
            print(f"Sent reminder to {client_email} for invoice #{invoice.id}")
        else:
            print(f"Failed to send reminder for invoice #{invoice.id}")

