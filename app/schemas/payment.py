from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PaymentBase(BaseModel):
    invoice_id: int
    amount: float
    method: str
    transaction_id: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    invoice_id: Optional[int] = None
    amount: Optional[float] = None
    method: Optional[str] = None
    transaction_id: Optional[str] = None

class PaymentResponse(PaymentBase):
    id: int
    payment_date: datetime

    class Config:
        orm_mode = True