from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel

class PurchaseEnum(str, Enum):
    bulk = 'bulk'
    warranty = 'warranty'

class PurchaseResponse(BaseModel):
    purchase_id: int
    purchase_type: PurchaseEnum
    purchase_date: datetime
    part_id: int

class PurchaseRequest(BaseModel):
    purchase_type: PurchaseEnum
    purchase_date: datetime
    part_id: int

class PurchaseUpdate(BaseModel):
    purchase_type: Optional[str] = None
    purchase_date: Optional[datetime] = None

class PurchaseDelete(BaseModel):
    purchase_id: str