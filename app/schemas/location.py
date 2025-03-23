from enum import Enum
from typing import Optional
from pydantic import BaseModel

class MarketEnum(str, Enum):
    north_america = "north_america"
    south_america = "south_america"
    latin_america = "latin_america"
    central_america = "central_america"
    north_africa = "north_africa"
    south_africa = "south_africa"
    european_union = "european_union"
    oceania = "oceania"
    middle_east = "middle_east"
    east_asia = "east_asia"
    south_asia = "south_asia"
    central_asia = "central_asia"

class LocationResponse(BaseModel):
    location_id: int
    market: MarketEnum
    country: str
    province: str
    city: str

class LocationRequest(BaseModel):
    market: MarketEnum
    country: str
    province: str
    city: str

class LocationUpdate(BaseModel):
    market: Optional[MarketEnum] = None
    country: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None

class LocationDelete(BaseModel):
    location_id: int