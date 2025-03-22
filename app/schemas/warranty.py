from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class WarrantyResponse(BaseModel):
    vehicle_id: int
    claim_key: int
    repair_date: datetime
    client_comment: str
    tech_comment: str
    part_id: int
    classified_failured: str
    location_id: int
    purchase_id: int

class WarrantyRequest(BaseModel):
    vehicle_id: int
    repair_date: datetime
    client_comment: str
    tech_comment: str
    part_id: int
    classified_failured: str
    location_id: int
    purchase_id: int

class WarrantyUpdate(BaseModel):
    vehicle_id: Optional[int] = None
    repair_date: Optional[datetime] = None
    client_comment: Optional[str] = None
    tech_comment: Optional[str] = None
    part_id: Optional[int] = None
    classified_failured: Optional[str] = None
    location_id: Optional[int] = None
    purchase_id: Optional[int] = None

class WarrantyDelete(BaseModel):
    claim_key: int