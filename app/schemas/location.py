from typing import Optional
from pydantic import BaseModel

class LocationResponse(BaseModel):
    location_id: int
    market: str
    country: str
    province: str
    city: str

class LocationRequest(BaseModel):
    market: str
    country: str
    province: str
    city: str

class LocationUpdate(BaseModel):
    market: Optional[str] = None
    country: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None

class LocationDelete(BaseModel):
    location_id: int