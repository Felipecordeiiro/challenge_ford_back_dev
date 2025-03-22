from datetime import datetime
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
    purchance_id: int

class WarrantyRequest(BaseModel):
    vehicle_id: int
    repair_date: datetime
    client_comment: str
    tech_comment: str
    part_id: int
    classified_failured: str
    location_id: int
    purchance_id: int

class WarrantyUpdate(BaseModel):
    repair_date: datetime
    client_comment: str
    tech_comment: str
    classified_failured: str

class WarrantyDelete(BaseModel):
    claim_key: int