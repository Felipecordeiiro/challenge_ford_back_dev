from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.configs.database import Base

class Part(Base):
    __tablename__ = 'parts'

    part_id = Column(Integer, primary_key=True, autoincrement=True)
    part_name = Column(String(255))
    last_id_purchase = Column(Integer, nullable=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.supplier_id'))

    purchases = relationship("Purchase", back_populates="part")