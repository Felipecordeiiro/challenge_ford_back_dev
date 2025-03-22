from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.configs.database import Base

class Vehicle(Base):
    __tablename__ = 'vehicles'

    vehicle_id = Column(Integer, primary_key=True, autoincrement=True)
    model = Column(String)
    prod_date = Column(DateTime)
    year = Column(Integer)
    propulsion = Column(String)
