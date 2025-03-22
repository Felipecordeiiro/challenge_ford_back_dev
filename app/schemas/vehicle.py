from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class PropulsionEnum(str, Enum):
    eletric = 'eletric'
    hybrid = 'hybrid'
    gas = 'gas'

class VehicleResponse(BaseModel):
    vehicle_id: int
    model: str
    prod_date: datetime
    year: int
    propulsion: PropulsionEnum

class VehicleRequest(BaseModel):
    model: str
    prod_date: datetime
    year: int
    propulsion: PropulsionEnum

class VehicleUpdate(BaseModel):
    model: Optional[str] = None
    prod_date: Optional[datetime] = None
    year: Optional[int] = None
    propulsion: Optional[PropulsionEnum] = PropulsionEnum.gas # Padrão gás

class VehicleDelete(BaseModel):
    vehicle_id: int