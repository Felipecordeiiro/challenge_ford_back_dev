from typing import Optional
from pydantic import BaseModel

class PartResponse(BaseModel):
    part_id: int
    part_name: str
    last_id_purchase: int
    supplier_id: int

class PartRequest(BaseModel):
    part_name: str
    last_id_purchase: int
    supplier_id: int

class PartUpdate(BaseModel):
    part_name: Optional[str] = None

class PartDelete(BaseModel):
    part_name: str