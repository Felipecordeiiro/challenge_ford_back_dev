from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.configs.database import Base

class Warranty(Base):
    __tablename__ = 'fact_warranties'

    vehicle_id = Column(Integer, ForeignKey('vehicles.vehicle_id'))
    claim_key = Column(Integer, autoincrement=True, primary_key=True)
    repair_date = Column(DateTime)
    client_comment = Column(String)
    tech_comment = Column(String)
    part_id = Column(Integer, ForeignKey('parts.part_id'))
    classified_failured = Column(String)
    location_id = Column(Integer, ForeignKey('locations.location_id'))
    purchase_id = Column(Integer, ForeignKey('purchases.purchase_id'))
