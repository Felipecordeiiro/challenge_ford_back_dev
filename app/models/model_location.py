from sqlalchemy import Column, Integer, String
from app.configs.database import Base

class Location(Base):
    __tablename__ = 'locations'

    location_id = Column(Integer, primary_key=True, autoincrement=True) 
    market = Column(String(50))
    country = Column(String(50))
    province = Column(String(50))
    city = Column(String(50))
