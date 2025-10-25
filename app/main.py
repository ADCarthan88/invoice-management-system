from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import StreamingResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import engine, get_db, Base
from app.routers import clients, invoices, payments
from app.models import client, invoice, payment  # Import models to create tables
from app.models.invoice import Invoice  # Import Invoice model specifically
from app.models.client import Client
from app.models.payment import Payment
from app.services.pdf_generation import generate_invoice_pdf
from app.services.payment_integration import process_stripe_payment, process_paypal_payment
from app.services.email_reminders import send_overdue_reminders
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import logging

app = FastAPI(title="Automated Invoice & Payment System", version="1.0.0")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Create database tables on startup
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(clients.router, prefix="/api", tags=["clients"])
app.include_router(invoices.router, prefix="/api", tags=["invoices"])
app.include_router(payments.router, prefix="/api", tags=["payments"])

@app.get("/")
def read_root():
    return RedirectResponse(url="/dashboard")

@app.get("/api")
def api_root():
    return {"message": "Welcome to the Automated Invoice & Payment System API"}

# Web Interface Routes
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    # Get dashboard statistics
    total_clients = db.query(Client).count()
    total_invoices = db.query(Invoice).count()
    total_revenue = db.query(func.sum(Invoice.amount)).scalar() or 0
    pending_invoices = db.query(Invoice).filter(Invoice.paid == False).count()
    
    # Get recent invoices
    recent_invoices = db.query(Invoice).order_by(Invoice.created_at.desc()).limit(5).all()
    
    stats = {
        "clients": total_clients,
        "invoices": total_invoices,
        "revenue": total_revenue,
        "pending": pending_invoices
    }
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "recent_invoices": recent_invoices
    })

@app.get("/clients", response_class=HTMLResponse)
def clients_page(request: Request, db: Session = Depends(get_db)):
    clients = db.query(Client).all()
    return templates.TemplateResponse("clients.html", {
        "request": request,
        "clients": clients
    })

@app.get("/clients/new", response_class=HTMLResponse)
def new_client_page(request: Request):
    return templates.TemplateResponse("client_form.html", {
        "request": request,
        "client": None
    })

@app.post("/clients/new")
async def create_client_web(request: Request, db: Session = Depends(get_db),
                           name: str = Form(...), email: str = Form(...),
                           phone: str = Form(""), address: str = Form("")):
    client_data = Client(name=name, email=email, phone=phone or None, address=address or None)
    db.add(client_data)
    db.commit()
    return RedirectResponse(url="/clients", status_code=303)

@app.get("/clients/{client_id}", response_class=HTMLResponse)
def client_detail(request: Request, client_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return templates.TemplateResponse("client_detail.html", {
        "request": request,
        "client": client
    })

@app.get("/api/dashboard/stats")
def dashboard_stats(db: Session = Depends(get_db)):
    total_clients = db.query(Client).count()
    total_invoices = db.query(Invoice).count()
    total_revenue = db.query(func.sum(Invoice.amount)).scalar() or 0
    pending_invoices = db.query(Invoice).filter(Invoice.paid == False).count()
    
    return {
        "clients": total_clients,
        "invoices": total_invoices,
        "revenue": float(total_revenue),
        "pending": pending_invoices
    }

# API routes for services
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

# Background task scheduler
scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def start_scheduler():
    # Schedule daily reminders at 9 AM
    scheduler.add_job(send_daily_reminders, "cron", hour=9)
    scheduler.start()
    logging.info("Scheduler started")

@app.on_event("shutdown")
async def shutdown_scheduler():
    scheduler.shutdown()
    logging.info("Scheduler stopped")

async def send_daily_reminders():
    """Send daily email reminders for overdue invoices"""
    db = next(get_db())
    try:
        send_overdue_reminders(db)
        logging.info("Daily reminders sent successfully")
    except Exception as e:
        logging.error(f"Error sending daily reminders: {e}")
    finally:
        db.close()