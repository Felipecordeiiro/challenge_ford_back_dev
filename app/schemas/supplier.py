from typing import Optional
from pydantic import BaseModel

class SupplierResponse(BaseModel):
    supplier_id: int
    supplier_name: str
    supplier_cpf: str
    location_id: int

class SupplierRequest(BaseModel):
    supplier_name: str
    supplier_cpf: str
    location_id: int

class SupplierUpdate(BaseModel):
    supplier_name: Optional[str] = None
    supplier_cpf: Optional[str] = None

class SupplierDelete(BaseModel):
    supplier_name: str