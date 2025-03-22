from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.configs.database import Base

class Purchase(Base):
    __tablename__ = 'purchases'

    purchase_id = Column(Integer, primary_key=True, autoincrement=True)
    purchase_type = Column(String(50))
    purchase_date = Column(DateTime)
    part_id = Column(Integer, ForeignKey('parts.part_id'))

    part = relationship("Part", back_populates="purchases")