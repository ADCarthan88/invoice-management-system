import stripe
from paypalrestsdk import Payment as PayPalPayment
import paypalrestsdk
from sqlalchemy.orm import Session
from app.models.payment import Payment
from app.models.invoice import Invoice
from app.config import STRIPE_SECRET_KEY, PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET  # Assuming config has these

# Configure Stripe
stripe.api_key = STRIPE_SECRET_KEY

# Configure PayPal
paypalrestsdk.configure({
    "mode": "sandbox",  # Change to "live" for production
    "client_id": PAYPAL_CLIENT_ID,
    "client_secret": PAYPAL_CLIENT_SECRET
})

def process_stripe_payment(invoice_id: int, amount: float, token: str, db: Session):
    """Process payment via Stripe."""
    try:
        charge = stripe.Charge.create(
            amount=int(amount * 100),  # Amount in cents
            currency="usd",
            source=token,
            description=f"Payment for invoice {invoice_id}"
        )
        # Create payment record
        payment = Payment(
            invoice_id=invoice_id,
            amount=amount,
            method="stripe",
            transaction_id=charge.id
        )
        db.add(payment)
        db.commit()
        # Update invoice if fully paid
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if invoice:
            invoice.paid = True
            db.commit()
        return {"status": "success", "transaction_id": charge.id}
    except stripe.error.StripeError as e:
        return {"status": "error", "message": str(e)}

def process_paypal_payment(invoice_id: int, amount: float, db: Session):
    """Process payment via PayPal."""
    payment = PayPalPayment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "transactions": [{
            "amount": {"total": f"{amount:.2f}", "currency": "USD"},
            "description": f"Payment for invoice {invoice_id}"
        }],
        "redirect_urls": {
            "return_url": "http://localhost:8000/success",
            "cancel_url": "http://localhost:8000/cancel"
        }
    })
    if payment.create():
        # Create payment record (assuming approval)
        pay_record = Payment(
            invoice_id=invoice_id,
            amount=amount,
            method="paypal",
            transaction_id=payment.id
        )
        db.add(pay_record)
        db.commit()
        # Update invoice
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if invoice:
            invoice.paid = True
            db.commit()
        return {"status": "success", "approval_url": payment.links[1].href}
    else:
        return {"status": "error", "message": payment.error}