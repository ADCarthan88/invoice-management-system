from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    amount = Column(Float, nullable=False)
    due_date = Column(DateTime, nullable=False)
    paid = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    description = Column(String(500), nullable=True)

    # Relationship to client
    client = relationship("Client", back_populates="invoices")
    # Relationship to payments
    payments = relationship("Payment", back_populates="invoice")