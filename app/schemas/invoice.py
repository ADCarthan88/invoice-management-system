from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .client import ClientResponse

class InvoiceBase(BaseModel):
    client_id: int
    amount: float
    due_date: datetime
    description: Optional[str] = None

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceUpdate(BaseModel):
    client_id: Optional[int] = None
    amount: Optional[float] = None
    due_date: Optional[datetime] = None
    paid: Optional[bool] = None
    description: Optional[str] = None

class InvoiceResponse(InvoiceBase):
    id: int
    paid: bool
    created_at: datetime
    client: ClientResponse

    class Config:
        orm_mode = True