# Classes auxiliares para respostas
from typing import List
from pydantic import BaseModel
from app.schemas.location import MarketEnum

class SupplierAnalytics(BaseModel):
    supplier_id: int
    supplier_name: str
    supplier_cpf: str
    location_id: int
    market: MarketEnum
    country: str
    province: str
    city: str
    total_parts: int
    total_purchases: int
    bulk_purchases: int
    warranty_purchases: int
    
class ProvinceAnalytics(BaseModel):
    province: str
    total_suppliers: int
    total_parts: int
    total_purchases: int
    bulk_percentage: float
    warranty_percentage: float
    suppliers_by_market: dict
    top_suppliers: List[SupplierAnalytics]