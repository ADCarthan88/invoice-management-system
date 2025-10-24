from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import engine, get_db, Base
from app.routers import clients, invoices, payments
from app.models import client, invoice, payment  # Import models to create tables
from app.services.pdf_generation import generate_invoice_pdf
from app.services.payment_integration import process_stripe_payment, process_paypal_payment
from app.services.email_reminders import send_overdue_reminders
import asyncio

app = FastAPI(title="Automated Invoice & Payment System", version="1.0.0")

# Create database tables on startup
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(clients.router, prefix="/clients", tags=["clients"])
app.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Automated Invoice & Payment System API"}

# Additional routes for services
@app.get("/invoices/{invoice_id}/pdf")
def download_invoice_pdf(invoice_id: int, db: Session = Depends(get_db)):
    invoice_obj = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice_obj:
        raise HTTPException(status_code=404, detail="Invoice not found")
    client_obj = invoice_obj.client
    pdf_buffer = generate_invoice_pdf(invoice_obj, client_obj)
    return StreamingResponse(pdf_buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=invoice_{invoice_id}.pdf"})

@app.post("/payments/stripe")
def create_stripe_payment(invoice_id: int, amount: float, token: str, db: Session = Depends(get_db)):
    result = process_stripe_payment(invoice_id, amount, token, db)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.post("/payments/paypal")
def create_paypal_payment(invoice_id: int, amount: float, db: Session = Depends(get_db)):
    result = process_paypal_payment(invoice_id, amount, db)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

# Background task for reminders (run periodically, e.g., daily)
@app.on_event("startup")
async def start_reminder_task():
    asyncio.create_task(run_reminders())

async def run_reminders():
    while True:
        # Run every 24 hours
        await asyncio.sleep(86400)
        # Assuming db session; in real app, use a proper way
        # For simplicity, this is placeholder; in production, use APScheduler or similar
        pass  # Implement proper scheduling