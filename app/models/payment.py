from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, default=func.now())
    method = Column(String(50), nullable=False)  # e.g., 'stripe', 'paypal', 'bank_transfer'
    transaction_id = Column(String(255), nullable=True)

    # Relationship to invoice
    invoice = relationship("Invoice", back_populates="payments")