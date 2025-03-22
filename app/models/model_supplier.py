from sqlalchemy import Column, Integer, String, ForeignKey
from app.configs.database import Base

class Supplier(Base):
    __tablename__ = 'suppliers'

    supplier_id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_name = Column(String(50))
    supplier_cpf = Column(String(20))
    location_id = Column(Integer, ForeignKey('locations.location_id'))